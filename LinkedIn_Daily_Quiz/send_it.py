import logging
import time
import requests

LINKEDIN_UGC_URL = "https://api.linkedin.com/v2/ugcPosts"
REQUEST_TIMEOUT = 15
MAX_RETRIES = 3
BACKOFF_BASE = 2

def _retryable(status):
    """
        Check if a given HTTP status code should trigger a retry.
        Returns True for transient errors like timeouts or rate limiting.
    """
    return status in (408, 429, 500, 502, 503, 504)

def _sleep_retry(attempt, resp):
    """
        Wait before retrying a request.
        - If the response includes a 'Retry-After' header, wait that many seconds.
        - Otherwise, wait an exponentially increasing number of seconds (2^attempt).
    """
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

def post_text_update(access_token, person_urn, message, visibility="CONNECTIONS"):
    """
        Send a plain-text post to LinkedIn using the UGC API.
        Args:
            access_token: OAuth access token for LinkedIn.
            person_urn: The LinkedIn person URN (must start with 'urn:li:person:').
            message: The text content to post.
            visibility: Who can see the post. Use 'PUBLIC' or 'CONNECTIONS' (default).
        Behavior:
            - Builds the request payload with the message.
            - Sends the post to LinkedIn.
            - Retries automatically on certain temporary errors (like 429 or 500).
            - Returns the HTTP response object (requests.Response).
            - Raises an error if all retries fail.
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
            resp = requests.post(
                LINKEDIN_UGC_URL,
                headers=headers,
                json=payload,
                timeout=REQUEST_TIMEOUT,
            )
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

    raise RuntimeError(f"Unknown LinkedIn posting failure: {last_exc}")