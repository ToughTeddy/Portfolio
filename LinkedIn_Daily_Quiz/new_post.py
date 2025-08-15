import json
from datetime import datetime, timedelta
from typing import Dict, List
from zoneinfo import ZoneInfo

def _load_questions(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list) or not data:
        raise RuntimeError("questions.json must be a non-empty JSON array")
    return data

def _format_question(entry: Dict) -> str:
    q = str(entry["question"]).strip()
    choices = entry.get("choices")
    if choices:
        choice_lines = "\n".join(f"- {str(c)}" for c in choices)
        return f"{q}\n{choice_lines}"
    return q

def build_daily_message(questions_path: str, *, offset_days: int = 0, tz: str = "UTC") -> str:
    questions = _load_questions(questions_path)
    try:
        base_date = datetime.now(ZoneInfo(tz)).date()
    except Exception:
        # Fallback if tz invalid on host
        base_date = datetime.utcnow().date()

    target_date = base_date + timedelta(days=offset_days)

    n = len(questions)
    today_idx = target_date.toordinal() % n
    yesterday_idx = (today_idx - 1) % n

    today_q = questions[today_idx]
    yesterday_q = questions[yesterday_idx]

    message = (
        "📌 Daily Python Quiz:\n\n"
        "🧠 Yesterday's Question:\n"
        f"{_format_question(yesterday_q)}\n\n"
        "Yesterday's Answer:\n"
        f"{yesterday_q.get('answer', '—')}\n\n"
        "💡 Today's Question:\n"
        f"{_format_question(today_q)}\n\n"
        "Spotted an issue or want to contribute a question? Reply or DM me!"
    )
    return message