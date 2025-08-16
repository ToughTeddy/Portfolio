import logging
import os
import tempfile

import azure.functions as func

LINKEDIN_UGC_URL = "https://api.linkedin.com/v2/ugcPosts"
REQUEST_TIMEOUT = 15  # seconds
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 2

CONTAINER = "quizdata"
BLOB_NAME = "questions.json"

app = func.FunctionApp()

# ---------- Config / validation ----------
REQUIRED_ENVS = ["ACCESS_TOKEN", "PERSON_URN", "STORAGE_CONNECTION_STRING"]

def _validate_config(access_token: str, person_urn: str, storage_conn: str) -> None:
    missing = []
    if not access_token:
        missing.append("ACCESS_TOKEN")
    if not person_urn:
        missing.append("PERSON_URN")
    if not storage_conn:
        missing.append("STORAGE_CONNECTION_STRING")
    if missing:
        raise RuntimeError(f"Missing required app settings: {', '.join(missing)}")
    if not person_urn.startswith("urn:li:person:"):
        raise RuntimeError("PERSON_URN must start with 'urn:li:person:'")

# ---------- Storage helper ----------
def _download_questions_to_tmp(storage_conn: str, container: str, blob_name: str) -> str:
    # Import here so missing packages don't break cold start/indexing
    from azure.storage.blob import BlobServiceClient
    from azure.core.exceptions import AzureError

    try:
        svc = BlobServiceClient.from_connection_string(storage_conn)
        blob = svc.get_blob_client(container=container, blob=blob_name)
        data = blob.download_blob().readall()
    except AzureError as e:
        raise RuntimeError(f"Failed to download blob '{container}/{blob_name}': {e}") from e

    tmp_path = os.path.join(tempfile.gettempdir(), "questions.json")
    with open(tmp_path, "wb") as f:
        f.write(data)
    return tmp_path

# ---------- Timer trigger ----------
@app.function_name(name="post_daily_quiz")
@app.schedule(schedule="0 0 14 * * *", arg_name="mytimer", run_on_startup=False, use_monitor=True)
def post_daily_quiz(mytimer: func.TimerRequest):
    logging.info("✅ post_daily_quiz triggered")
    if mytimer and mytimer.past_due:
        logging.warning("⏰ Timer is running late.")

    try:
        # Read individual env vars
        # Required envs (read inside the function for safe indexing)
        ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")
        PERSON_URN = os.getenv("PERSON_URN", "")
        STORAGE_CONN = os.getenv("STORAGE_CONNECTION_STRING", "")

        QUIZ_TZ = os.getenv("QUIZ_TZ", "America/Phoenix")
        OFFSET_DAYS = int(os.getenv("QUIZ_OFFSET_DAYS", "0"))
        VISIBILITY = os.getenv("QUIZ_VISIBILITY", "CONNECTIONS")

        # Validate required ones
        _validate_config(ACCESS_TOKEN, PERSON_URN, STORAGE_CONN)

        # Local imports for startup
        from new_post import build_daily_message
        from send_it import post_text_update

        questions_path = _download_questions_to_tmp(STORAGE_CONN, CONTAINER, BLOB_NAME)
        message = build_daily_message(questions_path, offset_days=OFFSET_DAYS, tz=QUIZ_TZ)

        resp = post_text_update(ACCESS_TOKEN, PERSON_URN, message, visibility=VISIBILITY)

        status = getattr(resp, "status_code", None)
        body_preview = getattr(resp, "text", "")[:500]
        if status and 200 <= status < 300:
            logging.info("🎉 LinkedIn post succeeded (%s). Preview: %s", status, body_preview)
        else:
            logging.error("❌ LinkedIn post failed (%s). Body: %s", status, body_preview)

    except Exception as e:
        logging.exception("🚨 post_daily_quiz failed: %s", e)
