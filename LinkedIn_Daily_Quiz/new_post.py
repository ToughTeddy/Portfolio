import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo
import re

from openai import OpenAI

OPENAI_MODEL = "gpt-5"

DEFAULT_TOPICS = [
    "Python basics",
    "Control flow",
    "Functions",
    "Data structures",
    "OOP in Python",
    "Modules & packages",
    "File I/O",
    "Exceptions",
    "Iterators & generators",
    "Comprehensions",
    "Decorators",
    "Typing & dataclasses",
    "Standard library (itertools, collections, pathlib)",
    "Asyncio",
    "Performance & Big-O (Python-flavored)"
]

CHOICE_LABELS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def _indent_code_block(code: str) -> str:
    """Indent code so it reads like a block in LinkedIn posts."""
    return "\n".join(f"    {line}" for line in code.strip("\n").splitlines())

def _split_question_and_code(q: str) -> tuple[str, str | None]:
    """
    Try to separate a natural-language question from an embedded code block.
    """
    lines = q.strip().splitlines()
    for i, ln in enumerate(lines):
        l = ln.lstrip()
        if i > 0 and (l.startswith("def ") or l.startswith("@") or l.startswith("class ") or l.startswith("import ")):
            head = "\n".join(lines[:i]).strip()
            code = "\n".join(lines[i:])
            return head, code
    return q.strip(), None

def _format_choices(choices: list[str]) -> str:
    out = []
    for idx, c in enumerate(choices):
        label = CHOICE_LABELS[idx] if idx < len(CHOICE_LABELS) else f"{idx+1}"
        out.append(f"{label}) {c}")
    return "\n".join(out)

def _answer_with_letter(entry: dict) -> str:
    ans = str(entry.get("answer", "—"))
    choices = entry.get("choices") or []
    try:
        idx = choices.index(ans)
        label = CHOICE_LABELS[idx] if idx < len(CHOICE_LABELS) else f"{idx+1}"
        return f"{ans} ({label})"
    except ValueError:
        return ans

def _json_loads_relaxed(s: str) -> Dict:
    try:
        return json.loads(s)
    except Exception:
        m = re.search(r"\{.*\}", s, flags=re.S)
        if not m:
            raise
        return json.loads(m.group(0))

def _get_client(api_key: Optional[str] = None) -> OpenAI:
    key = api_key or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OpenAI API key missing: pass api_key=... or set OPENAI_API_KEY")
    return OpenAI(api_key=key)

def _topic_for_day(date_ordinal: int, topics: List[str]) -> str:
    return topics[date_ordinal % len(topics)]


def _extract_response(resp) -> Dict:
    if hasattr(resp, "output_text") and resp.output_text:
        return json.loads(resp.output_text)
    try:
        blocks = getattr(resp, "output", []) or getattr(resp, "outputs", [])
        for b in blocks:
            for c in getattr(b, "content", []):
                txt = getattr(c, "text", None)
                if txt:
                    return json.loads(txt)
    except Exception as e:
        print(f"[extract_response] Failed to parse response content: {e}")
    return json.loads(str(resp))

def _validate_quiz(d: Dict) -> Dict:
    d.setdefault("question", "")
    d.setdefault("choices", [])
    d.setdefault("answer", "")
    d.setdefault("explanation", "")

    if d["choices"] and d["answer"] not in d["choices"]:
        norm = {c.strip(): c for c in d["choices"]}
        a = d["answer"].strip()
        if a in norm:
            d["answer"] = norm[a]
        else:
            d["answer"] = d["choices"][0]
    return d

def _generate_quiz_question(*, seed: int, topic: str, difficulty: str = "beginner",
                            api_key: Optional[str] = None) -> Dict:
    client = _get_client(api_key)

    system_prompt = (
        "You are a precise Python quiz generator. Output exactly one question.\n"
        "- Prefer practical, bite-sized concepts (no trick questions).\n"
        "- If you include choices, ensure exactly one correct answer.\n"
        "- Keep question under 280 characters if possible.\n"
        "- Return ONLY valid JSON with fields: question, choices (3–6), answer, explanation.\n"
        "- The 'answer' must be exactly one of 'choices'."
    )
    user_prompt = f"Generate one {difficulty} multiple-choice Python question on the topic: {topic}."

    try:
        resp = client.responses.create(
            model=OPENAI_MODEL,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            seed=int(seed),
        )
        data = _json_loads_relaxed(resp.output_text or "")
    except Exception as te:
        chat = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        data = _json_loads_relaxed(chat.choices[0].message.content)

    data = _validate_quiz(data)
    data.setdefault("choices", [])
    data.setdefault("explanation", "")
    return data

def _format_question(entry: dict) -> str:
    q = str(entry.get("question", "")).strip()
    choices = entry.get("choices") or []

    prompt, code = _split_question_and_code(q)

    parts = [prompt] if prompt else []

    if code:
        parts.append(_indent_code_block(code))

    if choices:
        if parts:
            parts.append("")
        parts.append(_format_choices(choices))

    return "\n".join(parts).rstrip()

def _question_for_date(the_date, *, topics: List[str], difficulty: str,
                       api_key: Optional[str]) -> Dict:
    date_ordinal = the_date.toordinal()
    topic = _topic_for_day(date_ordinal, topics)
    return _generate_quiz_question(seed=date_ordinal, topic=topic,
                                   difficulty=difficulty, api_key=api_key)

def build_daily_message(*, tz: str = "UTC", topics: Optional[List[str]] = None,
                        difficulty: str = "beginner", offset_days: int = 0,
                        api_key: Optional[str] = None) -> str:
    topics = topics or DEFAULT_TOPICS

    try:
        base_date = datetime.now(ZoneInfo(tz)).date()
    except Exception:
        base_date = datetime.utcnow().date()

    target_date = base_date + timedelta(days=offset_days)
    yesterday = target_date - timedelta(days=1)

    today_q = _question_for_date(target_date, topics=topics, difficulty=difficulty, api_key=api_key)
    yesterday_q = _question_for_date(yesterday, topics=topics, difficulty=difficulty, api_key=api_key)

    message = (
        "📌 Daily Python Quiz\n\n"
        "🧠 Yesterday's Question:\n"
        f"{_format_question(yesterday_q)}\n\n"
        "✅ Yesterday's Answer:\n"
        f"{_answer_with_letter(yesterday_q)}\n\n"
        "💡 Today's Question:\n"
        f"{_format_question(today_q)}\n\n"
        "Reply with your answer (A, B, C, …). Solution tomorrow!\n"
        "#Python #Quiz #OpenAI\n"
        "This is programmatically run post run daily using OpenAI's API and Azure.\n"
        "If you see an error, please msg me so I can refine the prompt.\n"
        "Thank You"
    )
    return message
