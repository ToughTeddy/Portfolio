import requests
from datetime import datetime, timezone, timedelta
import os
import json

import my_info as me


ACCESS_TOKEN = me.ACCESS_TOKEN
PERSON_URN = me.PERSON_URN
LINKEDIN_UGC_URL = "https://api.linkedin.com/v2/ugcPosts"

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0",
}

HERE = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_PATH = os.path.join(HERE, "questions.json")

with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
    QUESTIONS = json.load(f)

if not isinstance(QUESTIONS, list) or len(QUESTIONS) == 0:
    raise RuntimeError("questions.json must be a non-empty JSON array")

def format_question(entry: dict) -> str:
    q = str(entry["question"]).strip()
    choices = entry.get("choices")
    if choices:
        choice_lines = "\n".join(f"- {str(c)}" for c in choices)
        return f"{q}\n{choice_lines}"
    return q

# switch which today_ord variables are commented out to post today's and tomorrow's posts.
# today's post
today_ord = datetime.now(timezone.utc).date().toordinal()
# tomorrow's post
# today_ord = (datetime.now(timezone.utc).date() + timedelta(days=1)).toordinal()
n = len(QUESTIONS)
today_idx = today_ord % n
yesterday_idx = (today_idx - 1) % n

today_q = QUESTIONS[today_idx]
yesterday_q = QUESTIONS[yesterday_idx]

message = (
    "📌 Daily Python Quiz:\n\n"
    "🧠 Yesterday's Question:\n"
    f"{format_question(yesterday_q)}\n\n"
    "Yesterday's Answer:\n"
    f"{yesterday_q.get('answer', '—')}\n\n"
    "💡 Today's Question:\n"
    f"{format_question(today_q)}\n\n"
    "Spotted an issue or want to contribute a question? Reply or DM me!"
)

payload = {
    "author": PERSON_URN,
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {"text": message},
            "shareMediaCategory": "NONE",
        }
    },
    "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "CONNECTIONS"},
}

resp = requests.post(LINKEDIN_UGC_URL, headers=HEADERS, json=payload)

print(resp.status_code)
print(resp.text)

try:
    urn = resp.json()["id"]
    print(f"https://www.linkedin.com/feed/update/{urn}")
except Exception:
    pass
