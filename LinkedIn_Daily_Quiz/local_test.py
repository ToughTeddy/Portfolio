import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo

try:
    import my_info as me
except ImportError:
    me = None

import new_post as new
import send_it as send

HERE = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_PATH = os.path.join(HERE, "questions.json")


def getenv(name, default=None):
    return os.getenv(name, default)


def get_cfg():
    cfg = {
        "OPENAI_KEY": getattr(me, "OPENAI_KEY", None) or getenv("OPENAI_KEY") or getenv("OPENAI_API_KEY"),
        "ACCESS_TOKEN": getattr(me, "ACCESS_TOKEN", None) or getenv("ACCESS_TOKEN"),
        "PERSON_URN": getattr(me, "PERSON_URN", None) or getenv("PERSON_URN"),
        "TZ": getattr(me, "QUIZ_TZ", None) or getenv("QUIZ_TZ", "America/Phoenix"),
        "DIFFICULTY": getattr(me, "QUIZ_DIFFICULTY", None) or getenv("QUIZ_DIFFICULTY", "beginner"),
        "OFFSET_DAYS": int(getattr(me, "QUIZ_OFFSET_DAYS", None) or getenv("QUIZ_OFFSET_DAYS", "0")),
        "VISIBILITY": getattr(me, "QUIZ_VISIBILITY", None) or getenv("QUIZ_VISIBILITY", "CONNECTIONS"),
        "MODEL": getattr(me, "QUIZ_OPENAI_MODEL", None) or getenv("QUIZ_OPENAI_MODEL", "gpt-5"),
    }
    missing = []
    if not cfg["ACCESS_TOKEN"]:
        missing.append("ACCESS_TOKEN")
    if not cfg["PERSON_URN"]:
        missing.append("PERSON_URN")
    if not cfg["OPENAI_KEY"]:
        missing.append("OPENAI_KEY (or OPENAI_API_KEY)")
    if missing:
        raise RuntimeError(f"Missing required settings: {', '.join(missing)}")
    return cfg


def load_questions_local():
    if not os.path.exists(QUESTIONS_PATH):
        return []
    with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_questions_local(items):
    with open(QUESTIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)


def append_question_local(item):
    items = load_questions_local()
    items.append(item)
    save_questions_local(items)
    return items


def main():
    cfg = get_cfg()

    # Yesterday’s entry
    all_items = load_questions_local()
    if all_items:
        yesterday_entry = all_items[-1]
    else:
        yesterday_entry = {"question": "", "choices": [], "answer": "—", "explanation": ""}

    # Today’s entry
    target_date = datetime.now(ZoneInfo(cfg["TZ"])).date()
    today_q = new._question_for_date(
        target_date,
        topics=new.DEFAULT_TOPICS,
        difficulty=cfg["DIFFICULTY"],
        api_key=cfg["OPENAI_KEY"],
        model=cfg["MODEL"],
    )

    # Append locally
    append_question_local(today_q)

    # Build message
    message = (
        "📌 Daily Python Quiz\n\n"
        "✅ Yesterday's Answer:\n"
        f"{new._answer_with_letter(yesterday_entry)}\n\n"
        "💡 Today's Question:\n"
        f"{new._format_question(today_q)}\n\n"
        "Reply with your answer (A, B, C, …). Solution tomorrow!\n"
        "#Python #Quiz #OpenAI\n"
        "This is a LOCAL test run."
    )

    print("\n=== Preview of message to post ===\n")
    print(message)
    print("\n=== End preview ===\n")

    # Post it
    resp = send.post_text_update(cfg["ACCESS_TOKEN"], cfg["PERSON_URN"], message, visibility=cfg["VISIBILITY"])

    print(f"Status: {getattr(resp, 'status_code', None)}")
    print(f"Body (first 500 chars): {getattr(resp, 'text', '')[:500]}")

    try:
        urn = resp.json().get("id")
        if urn:
            print(f"Post URL: https://www.linkedin.com/feed/update/{urn}")
        else:
            print("No 'id' found in LinkedIn response JSON.")
    except Exception as e:
        print(f"Failed to parse LinkedIn response JSON: {e}")


if __name__ == "__main__":
    main()