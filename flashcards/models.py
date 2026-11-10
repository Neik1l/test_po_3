"""Типы данных приложения для языковых флэш-карт."""
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Flashcard:
    id: int
    front: str
    back: str
    language: str = "Английский"


@dataclass(frozen=True, slots=True)
class AnswerResult:
    card_id: int
    entered_answer: str
    correct_answer: str
    is_correct: bool


@dataclass(frozen=True, slots=True)
class SessionSummary:
    total: int
    answered: int
    correct: int
    incorrect: int
    accuracy_percent: float
