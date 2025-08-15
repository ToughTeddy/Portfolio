import os
import my_info as me
import new_post as new
import send_it as send

HERE = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_PATH = os.path.join(HERE, "questions.json")

# Build today's message (use offset_days=1 to test tomorrow's)
message = new.build_daily_message(QUESTIONS_PATH, offset_days=0, tz="America/Phoenix")

# Post it
resp = send.post_text_update(me.ACCESS_TOKEN, me.PERSON_URN, message, visibility="CONNECTIONS")

print(resp.status_code)
print(resp.text)

try:
    urn = resp.json()["id"]
    print(f"https://www.linkedin.com/feed/update/{urn}")
except Exception:
    pass
