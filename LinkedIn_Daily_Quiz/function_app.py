import logging
import os
import tempfile

import azure.functions as func

app = func.FunctionApp()

# ---------- Config / validation ----------
REQUIRED_ENVS = ["ACCESS_TOKEN", "PERSON_URN", "STORAGE_CONNECTION_STRING"]

def _validate_config() -> dict:
    cfg = {
        "ACCESS_TOKEN": os.getenv("ACCESS_TOKEN", ""),
        "PERSON_URN": os.getenv("PERSON_URN", ""),
        "STORAGE_CONN": os.getenv("STORAGE_CONNECTION_STRING", ""),
        "CONTAINER": os.getenv("CONTAINER_NAME", "quizdata"),
        "BLOB_NAME": os.getenv("BLOB_NAME", "questions.json"),
        "QUIZ_TZ": os.getenv("QUIZ_TZ", "America/Phoenix"),
        "OFFSET_DAYS": int(os.getenv("QUIZ_OFFSET_DAYS", "0")),
        "VISIBILITY": os.getenv("QUIZ_VISIBILITY", "CONNECTIONS"),
    }

    missing = [k for k in REQUIRED_ENVS if not cfg.get(k)]
    if missing:
        raise RuntimeError(f"Missing required app settings: {', '.join(missing)}")
    if not cfg["PERSON_URN"].startswith("urn:li:person:"):
        raise RuntimeError("PERSON_URN must start with 'urn:li:person:'")
    return cfg

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
        cfg = _validate_config()

        # Local imports keep startup resilient
        from new_post import build_daily_message
        from send_it import post_text_update

        questions_path = _download_questions_to_tmp(
            cfg["STORAGE_CONN"], cfg["CONTAINER"], cfg["BLOB_NAME"]
        )
        message = build_daily_message(
            questions_path, offset_days=cfg["OFFSET_DAYS"], tz=cfg["QUIZ_TZ"]
        )

        resp = post_text_update(
            cfg["ACCESS_TOKEN"],
            cfg["PERSON_URN"],
            message,
            visibility=cfg["VISIBILITY"],
        )

        status = getattr(resp, "status_code", None)
        body_preview = getattr(resp, "text", "")[:500]
        if status and 200 <= status < 300:
            logging.info("🎉 LinkedIn post succeeded (%s). Preview: %s", status, body_preview)
        else:
            logging.error("❌ LinkedIn post failed (%s). Body: %s", status, body_preview)

    except Exception as e:
        logging.exception("🚨 post_daily_quiz failed: %s", e)

# ---------- Simple health check ----------
@app.function_name(name="ping")
@app.route(route="ping", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def ping(req: func.HttpRequest):
    return func.HttpResponse("ok", status_code=200)