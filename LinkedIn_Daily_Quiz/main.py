import os
import my_info as me
import new_post as new
import send_it as send

HERE = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_PATH = os.path.join(HERE, "questions.json")

# Build today's message
message = new.build_daily_message(
    tz="America/Phoenix",
    difficulty="beginner",
    offset_days=0,
    api_key=me.OPENAI_KEY,
)

# Post it
resp = send.post_text_update(me.ACCESS_TOKEN, me.PERSON_URN, message, visibility="CONNECTIONS")

print(resp.status_code)
print(resp.text)

try:
    urn = resp.json()["id"]
    print(f"https://www.linkedin.com/feed/update/{urn}")
except Exception as e:
    print(f"Failed to parse LinkedIn response JSON: {e}")
