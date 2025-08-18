import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo

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

client = OpenAI()

def _topic_for_day():
    pass

def _extract_response():
    pass

def _generate_quiz_question():
    pass

def _format_question():
    pass

def _question_for_date():
    pass

def main():
    pass
