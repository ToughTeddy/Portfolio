from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from openai_prompt import OpenAIPrompt
from quiz_store import load_questions, append_question

OPENAI_MODEL = "gpt-5"

DEFAULT_CONTAINER = "quizdata"
DEFAULT_BLOB = "questions.json"

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

# --- Format questions and answers for LinkedIn posts ---

def _indent_code_block(code):
    """
        Make code blocks look like LinkedIn post formatting
    """
    return "\n".join(f"    {line}" for line in code.strip("\n").splitlines())


def _split_question_and_code(q):
    """
        Split a question into plain text and optional code.
    """
    lines = q.strip().splitlines()
    for i, ln in enumerate(lines):
        l = ln.lstrip()
        if i > 0 and (l.startswith("def ") or l.startswith("@") or l.startswith("class ") or l.startswith("import ")):
            head = "\n".join(lines[:i]).strip()
            code = "\n".join(lines[i:])
            return head, code
    return q.strip(), None

def _sanitize_one_line(s: str) -> str:
    """
        Collapse whitespace so choices always stay on one line
    """
    return " ".join(str(s).split())

def _format_choices(choices):
    """
        Add labels like A), B), C) to each choice
    """
    out = []
    for idx, c in enumerate(choices):
        label = CHOICE_LABELS[idx] if idx < len(CHOICE_LABELS) else f"{idx+1}"
        out.append(f"{label}) {_sanitize_one_line(c)}")
    return "\n".join(out)


def _answer_with_letter(entry):
    """
        Show yesterday’s answer with the answer text and its letter
    """
    ans = str(entry.get("answer", "—"))
    choices = entry.get("choices") or []
    try:
        idx = choices.index(ans)
        label = CHOICE_LABELS[idx] if idx < len(CHOICE_LABELS) else f"{idx+1}"
        return f"{ans} ({label})"
    except ValueError:
        return ans

def _answer_letter_first(entry):
    """
        Alternate format: letter first, then the answer text
    """
    ans = str(entry.get("answer", "—"))
    choices = entry.get("choices") or []
    try:
        idx = choices.index(ans)
        label = CHOICE_LABELS[idx] if idx < len(CHOICE_LABELS) else f"{idx+1}"
        return f"{label}) {_sanitize_one_line(ans)}"
    except ValueError:
        return _sanitize_one_line(ans)

def _format_question(entry):
    """
        Build the final display of a question (with code and choices, if any)
    """
    q = str(entry.get("question", "")).strip()
    choices = entry.get("choices") or []

    prompt, code = _split_question_and_code(q)
    parts = []

    if prompt:
        parts.append(prompt)

    if code:
        parts.append(_indent_code_block(code))

    if choices:
        parts.append("Choices:")
        parts.append(_format_choices(choices))

    return "\n".join(parts).rstrip()


# --- Pick topics and prepare quiz questions ---

def _topic_for_day(date_ordinal, topics):
    """
        Work out which topic to use on a given date
    """
    return topics[date_ordinal % len(topics)]


def _validate_quiz(d):
    """
        Make sure the generated question has all required fields
    """
    d.setdefault("question", "")
    d.setdefault("choices", [])
    d.setdefault("answer", "")
    d.setdefault("explanation", "")
    if d["choices"] and d["answer"] not in d["choices"]:
        norm = {c.strip(): c for c in d["choices"]}
        a = d["answer"].strip()
        d["answer"] = norm.get(a, d["choices"][0])
    return d


def _generate_quiz_question(
    *,
    seed,
    topic,
    difficulty="beginner",
    api_key=None,
    model=OPENAI_MODEL,
):
    """
        Use OpenAI to generate a single quiz question
    """
    system_prompt = (
        "You are a precise Python quiz generator. Output exactly one question.\n"
        "- Prefer practical, bite-sized concepts (no trick questions).\n"
        "- Include 4 multiple-choice options; ensure exactly one correct answer.\n"
        "- Keep the question under 280 characters if possible.\n"
        "- Choices must be ONE LINE each (no newlines) and MUST NOT include letters like 'A.'; "
        "just the option text. We'll label them later.\n"
        "- Return ONLY valid JSON with fields: question, choices (exactly 4), answer, explanation.\n"
        "- The 'answer' value must exactly match one item in 'choices'."
    )
    user_prompt = f"Generate one {difficulty} multiple-choice Python question on the topic: {topic}."

    prompt_client = OpenAIPrompt(api_key=api_key, model=model)
    data = prompt_client.generate_json(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        seed=seed,
    )

    data = _validate_quiz(data or {})
    data.setdefault("choices", [])
    data.setdefault("explanation", "")
    return data


def _question_for_date(
    the_date,
    *,
    topics,
    difficulty,
    api_key=None,
    model=OPENAI_MODEL,
):
    """
        Generate a question for a specific date
    """
    date_ordinal = the_date.toordinal()
    topic = _topic_for_day(date_ordinal, topics)
    return _generate_quiz_question(
        seed=date_ordinal,
        topic=topic,
        difficulty=difficulty,
        api_key=api_key,
        model=model,
    )


# --- Main function: put everything together for the LinkedIn post ---

def build_daily_message(
    *,
    tz="UTC",
    topics=None,
    difficulty="beginner",
    offset_days=0,
    api_key=None,
    model=OPENAI_MODEL,
    container=DEFAULT_CONTAINER,
    blob=DEFAULT_BLOB,
):
    """
        Build the LinkedIn post content, show yesterday’s answer,
        generate today’s question, and save it
    """
    topics = topics or DEFAULT_TOPICS

    try:
        base_date = datetime.now(ZoneInfo(tz)).date()
    except Exception:
        from datetime import datetime as _dt
        base_date = _dt.utcnow().date()

    target_date = base_date + timedelta(days=offset_days)

    # 1) Load yesterday from blob (last saved entry)
    all_items = load_questions(container, blob)
    if all_items:
        yesterday_entry = all_items[-1]
    else:
        yesterday_entry = {"question": "", "choices": [], "answer": "—", "explanation": ""}

    # 2) Generate today's question
    today_q = _question_for_date(
        target_date, topics=topics, difficulty=difficulty, api_key=api_key, model=model
    )

    # 3) Append today's question to storage
    append_question(container, blob, today_q)

    # 4) Build message
    divider = "—" * 24
    message = (
        "📌 Daily Python Quiz\n\n"
        "✅ Yesterday's Answer:\n"
        f"{_answer_letter_first(yesterday_entry)}\n\n"
        f"{divider}\n\n"
        "💡 Today's Question:\n"
        f"{_format_question(today_q)}\n\n"
        "Reply with your answer (A, B, C, …). Solution tomorrow!\n"
        "#Python #Quiz #OpenAI\n"
        "This is programmatically run post daily using OpenAI's API and Azure."
    )
    return message