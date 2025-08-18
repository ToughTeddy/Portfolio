import logging
import time
from typing import Optional

import requests

LINKEDIN_UGC_URL = "https://api.linkedin.com/v2/ugcPosts"
REQUEST_TIMEOUT = 15
MAX_RETRIES = 3
BACKOFF_BASE = 2

def _retryable(status: int) -> bool:
    return status in (408, 429, 500, 502, 503, 504)

def _sleep_retry(attempt: int, resp: Optional[requests.Response]) -> None:
    if resp is not None:
        ra = resp.headers.get("Retry-After")
        if ra:
            try:
                wait = int(ra)
                logging.warning("Retry-After: sleeping %ss", wait)
                time.sleep(wait)
                return
            except ValueError:
                pass
    wait = BACKOFF_BASE ** attempt
    logging.warning("Retrying in %ss (attempt %s/%s)...", wait, attempt, MAX_RETRIES)
    time.sleep(wait)

def post_text_update(access_token: str, person_urn: str, message: str, visibility: str = "CONNECTIONS"):
    """
    visibility: 'PUBLIC' or 'CONNECTIONS'
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    payload = {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": message},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": visibility},
    }

    last_exc = None
    resp = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(LINKEDIN_UGC_URL, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
            if 200 <= resp.status_code < 300:
                return resp

            logging.warning("LinkedIn %s: %s", resp.status_code, resp.text[:500])
            if _retryable(resp.status_code) and attempt < MAX_RETRIES:
                _sleep_retry(attempt, resp)
                continue
            return resp

        except requests.Timeout as e:
            last_exc = e
            logging.error("Timeout posting to LinkedIn: %s", e)
            if attempt < MAX_RETRIES:
                _sleep_retry(attempt, None)
                continue
            raise
        except requests.RequestException as e:
            last_exc = e
            logging.error("Request error posting to LinkedIn: %s", e)
            if attempt < MAX_RETRIES:
                _sleep_retry(attempt, None)
                continue
            raise

    # Shouldn’t reach here
    raise RuntimeError(f"Unknown LinkedIn posting failure: {last_exc}")