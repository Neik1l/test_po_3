"""Правила карточек, прохождения сессий и расчёта статистики."""
from __future__ import annotations

import unicodedata
from collections.abc import Callable, Iterable
from dataclasses import asdict

from .models import AnswerResult, Flashcard, SessionSummary


def _required_text(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Поле «{name}» должно содержать непустой текст")
    return value.strip()


def _normalize_answer(value: str) -> str:
    return unicodedata.normalize("NFKC", value).strip().casefold()


class StudySession:
    """Прохождение набора карточек в заданном порядке."""

    def __init__(
        self,
        cards: list[Flashcard],
        on_finished: Callable[[SessionSummary], None] | None = None,
    ) -> None:
        if not cards:
            raise ValueError("Нельзя запустить сессию без карточек")
        self._cards = tuple(cards)
        self._answers: list[AnswerResult] = []
        self._on_finished = on_finished

    @property
    def current_card(self) -> Flashcard | None:
        if self.is_finished:
            return None
        return self._cards[len(self._answers)]

    @property
    def is_finished(self) -> bool:
        return len(self._answers) == len(self._cards)

    @property
    def answers(self) -> tuple[AnswerResult, ...]:
        return tuple(self._answers)

    @property
    def summary(self) -> SessionSummary:
        answered = len(self._answers)
        correct = sum(answer.is_correct for answer in self._answers)
        return SessionSummary(
            total=len(self._cards),
            answered=answered,
            correct=correct,
            incorrect=answered - correct,
            accuracy_percent=round(100.0 * correct / answered, 2) if answered else 0.0,
        )

    def submit_answer(self, answer: str) -> AnswerResult:
        if self.is_finished:
            raise RuntimeError("Сессия уже завершена")
        provided = _required_text(answer, "ответ")
        card = self._cards[len(self._answers)]
        result = AnswerResult(
            card_id=card.id,
            entered_answer=provided,
            correct_answer=card.back,
            is_correct=_normalize_answer(provided) == _normalize_answer(card.back),
        )
        self._answers.append(result)
        if self.is_finished and self._on_finished is not None:
            self._on_finished(self.summary)
        return result


class FlashcardTrainer:
    """Менеджер карточек и архив законченных учебных сессий."""

    def __init__(self) -> None:
        self._cards: dict[int, Flashcard] = {}
        self._next_id = 1
        self._history: list[SessionSummary] = []

    def create_card(self, front: str, back: str, language: str = "Английский") -> Flashcard:
        card = Flashcard(
            id=self._next_id,
            front=_required_text(front, "вопрос"),
            back=_required_text(back, "ответ"),
            language=_required_text(language, "язык"),
        )
        self._cards[card.id] = card
        self._next_id += 1
        return card

    def update_card(
        self,
        card_id: int,
        *,
        front: str | None = None,
        back: str | None = None,
        language: str | None = None,
    ) -> Flashcard:
        current = self.get_card(card_id)
        updated = Flashcard(
            id=card_id,
            front=_required_text(front, "вопрос") if front is not None else current.front,
            back=_required_text(back, "ответ") if back is not None else current.back,
            language=_required_text(language, "язык") if language is not None else current.language,
        )
        self._cards[card_id] = updated
        return updated

    def get_card(self, card_id: int) -> Flashcard:
        if isinstance(card_id, bool) or not isinstance(card_id, int) or card_id not in self._cards:
            raise KeyError(f"Карточка с ID {card_id} не найдена")
        return self._cards[card_id]

    def list_cards(self) -> list[Flashcard]:
        return list(self._cards.values())

    @property
    def history(self) -> tuple[SessionSummary, ...]:
        return tuple(self._history)

    def start_session(self, card_ids: Iterable[int] | None = None) -> StudySession:
        if card_ids is None:
            cards = self.list_cards()
        else:
            ids = list(card_ids)
            if len(ids) != len(set(ids)):
                raise ValueError("Нельзя повторно включать одну карточку в одну сессию")
            cards = [self.get_card(card_id) for card_id in ids]
        return StudySession(cards, self._history.append)

    def to_dict(self) -> dict:
        return {
            "next_id": self._next_id,
            "cards": [asdict(card) for card in self.list_cards()],
            "history": [asdict(result) for result in self.history],
        }

    @classmethod
    def from_dict(cls, data: dict) -> FlashcardTrainer:
        if not isinstance(data, dict):
            raise ValueError("Формат данных должен быть объектом JSON")
        trainer = cls()
        for raw in data.get("cards", []):
            try:
                card = Flashcard(
                    id=raw["id"],
                    front=_required_text(raw["front"], "вопрос"),
                    back=_required_text(raw["back"], "ответ"),
                    language=_required_text(raw["language"], "язык"),
                )
            except (KeyError, TypeError) as error:
                raise ValueError("Повреждённая запись карточки") from error
            if not isinstance(card.id, int) or isinstance(card.id, bool) or card.id <= 0 or card.id in trainer._cards:
                raise ValueError("Некорректные идентификаторы карточек")
            trainer._cards[card.id] = card
        history = data.get("history", [])
        if not isinstance(history, list):
            raise ValueError("История сессий должна быть списком")
        for raw in history:
            try:
                summary = SessionSummary(**raw)
            except (TypeError, KeyError) as error:
                raise ValueError("Повреждённая история сессий") from error
            if (not isinstance(summary.total, int) or summary.total <= 0 or
                    not isinstance(summary.answered, int) or summary.answered != summary.total or
                    not isinstance(summary.correct, int) or not isinstance(summary.incorrect, int) or
                    summary.correct < 0 or summary.incorrect < 0 or
                    summary.correct + summary.incorrect != summary.total or
                    not isinstance(summary.accuracy_percent, (int, float)) or
                    abs(summary.accuracy_percent - round(100 * summary.correct / summary.total, 2)) > 0.01):
                raise ValueError("Некорректная статистика в истории")
            trainer._history.append(summary)
        next_id = data.get("next_id", max(trainer._cards, default=0) + 1)
        if not isinstance(next_id, int) or isinstance(next_id, bool) or next_id <= max(trainer._cards, default=0):
            raise ValueError("Некорректный следующий идентификатор")
        trainer._next_id = next_id
        return trainer
