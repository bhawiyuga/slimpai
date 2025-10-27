"""
Quiz Bank Module
Organized question banks for different topics
"""

from .fractions import FRACTIONS_BANK
from .multiplication import MULTIPLICATION_BANK
from .division import DIVISION_BANK

# Combine all question banks
QUESTION_BANK = {
    "Fractions": FRACTIONS_BANK,
    "Multiplication": MULTIPLICATION_BANK,
    "Division": DIVISION_BANK
}


def get_baseline_test(topic: str) -> list:
    """Get baseline test questions for a topic"""
    return QUESTION_BANK.get(topic, {}).get("baseline", [])


def get_lesson_content(topic: str, lesson_name: str) -> dict:
    """Get lesson content and quiz for a specific lesson"""
    lessons = QUESTION_BANK.get(topic, {}).get("lessons", {})
    return lessons.get(lesson_name, {})


def get_available_topics() -> list:
    """Get list of available topics"""
    return list(QUESTION_BANK.keys())


def get_all_lessons(topic: str) -> list:
    """Get list of all lesson names for a topic"""
    lessons = QUESTION_BANK.get(topic, {}).get("lessons", {})
    return list(lessons.keys())
