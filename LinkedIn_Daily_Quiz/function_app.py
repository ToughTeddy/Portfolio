import logging
import os

import azure.functions as func

app = func.FunctionApp()

# ---------- Config / validation ----------
REQUIRED_ENVS = ["ACCESS_TOKEN", "PERSON_URN"]

def _validate_config(access_token: str, person_urn: str, openai_key: str | None) -> None:
    """
        Check that the required environment values are set and valid.
        - ACCESS_TOKEN and PERSON_URN must exist
        - PERSON_URN must start with 'urn:li:person:'
        - An OpenAI API key must be provided
        Raises RuntimeError if something is missing or invalid.
    """
    missing = []
    if not access_token:
        missing.append("ACCESS_TOKEN")
    if not person_urn:
        missing.append("PERSON_URN")
    if missing:
        raise RuntimeError(f"Missing required app settings: {', '.join(missing)}")
    if not person_urn.startswith("urn:li:person:"):
        raise RuntimeError("PERSON_URN must start with 'urn:li:person:'")
    # OpenAI key is required for generating the quiz
    if not openai_key:
        raise RuntimeError("OpenAI API key missing: set OPENAI_API_KEY or OPENAI_KEY")

# ---------- Timer trigger ----------
@app.function_name(name="post_daily_quiz")
@app.schedule(schedule="0 0 14 * * *", arg_name="mytimer", run_on_startup=False, use_monitor=True)
def post_daily_quiz(mytimer: func.TimerRequest):
    """
        Azure Function that runs every day at 2:00 PM UTC.
        1. Checks environment variables for configuration
        2. Uses OpenAI to generate today’s quiz question
        3. Appends the new question to storage
        4. Builds a LinkedIn post with yesterday’s answer and today’s question
        5. Posts the message to LinkedIn using the API
        Logs whether the post succeeded or failed.
    """
    logging.info("✅ post_daily_quiz triggered")
    if mytimer and mytimer.past_due:
        logging.warning("⏰ Timer is running late.")

    try:
        # Pull settings from environment variables
        ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")
        PERSON_URN = os.getenv("PERSON_URN", "")
        OPENAI_KEY = os.getenv("OPENAI_KEY") or os.getenv("OPENAI_API_KEY")

        QUIZ_TZ = os.getenv("QUIZ_TZ", "America/Phoenix")
        QUIZ_DIFFICULTY = os.getenv("QUIZ_DIFFICULTY", "beginner")
        OFFSET_DAYS = int(os.getenv("QUIZ_OFFSET_DAYS", "0"))
        VISIBILITY = os.getenv("QUIZ_VISIBILITY", "CONNECTIONS")
        QUIZ_OPENAI_MODEL = os.getenv("QUIZ_OPENAI_MODEL", "gpt-5")

        _validate_config(ACCESS_TOKEN, PERSON_URN, OPENAI_KEY)

        from new_post import build_daily_message
        from send_it import post_text_update

        # Build the daily quiz post (yesterday’s answer + today’s question)
        message = build_daily_message(
            tz=QUIZ_TZ,
            difficulty=QUIZ_DIFFICULTY,
            offset_days=OFFSET_DAYS,
            api_key=OPENAI_KEY,
            model=QUIZ_OPENAI_MODEL,
        )

        # Post the message to LinkedIn
        resp = post_text_update(ACCESS_TOKEN, PERSON_URN, message, visibility=VISIBILITY)

        status = getattr(resp, "status_code", None)
        body_preview = getattr(resp, "text", "")[:500]

        if status and 200 <= status < 300:
            try:
                urn = resp.json().get("id")
                post_url = f"https://www.linkedin.com/feed/update/{urn}" if urn else "(no id in response)"
                logging.info("🎉 LinkedIn post succeeded (%s). URL: %s | Body: %s", status, post_url, body_preview)
            except Exception as e:
                logging.info("🎉 LinkedIn post succeeded (%s). Body: %s (URL parse failed: %s)", status, body_preview, e)
        else:
            logging.error("❌ LinkedIn post failed (%s). Body: %s", status, body_preview)

    except Exception as e:
        logging.exception("🚨 post_daily_quiz failed: %s", e)
