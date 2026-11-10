"""Консольный интерфейс: добавление, редактирование, занятия, статистика."""
from __future__ import annotations

import argparse
from pathlib import Path

from .storage import JsonStorage
from .trainer import FlashcardTrainer


def _add_card(trainer: FlashcardTrainer, storage: JsonStorage) -> None:
    front = input("Слово / вопрос: ")
    back = input("Перевод / ответ: ")
    language = input("Язык [Английский]: ").strip() or "Английский"
    card = trainer.create_card(front, back, language)
    storage.save(trainer)
    print(f"Карточка №{card.id} создана")


def _edit_card(trainer: FlashcardTrainer, storage: JsonStorage) -> None:
    card_id = int(input("Введите ID карточки: "))
    card = trainer.get_card(card_id)
    print("Оставьте поле пустым, чтобы не менять значение")
    front = input(f"Вопрос [{card.front}]: ").strip()
    back = input(f"Ответ [{card.back}]: ").strip()
    language = input(f"Язык [{card.language}]: ").strip()
    trainer.update_card(
        card_id,
        front=front if front else None,
        back=back if back else None,
        language=language if language else None,
    )
    storage.save(trainer)
    print("Карточка обновлена")


def _list_cards(trainer: FlashcardTrainer) -> None:
    cards = trainer.list_cards()
    if not cards:
        print("Карточек пока нет")
        return
    for card in cards:
        print(f"#{card.id} | {card.language} | {card.front} → {card.back}")


def _study(trainer: FlashcardTrainer, storage: JsonStorage) -> None:
    session = trainer.start_session()
    print(f"Начата сессия, карточек: {session.summary.total}")
    while not session.is_finished:
        card = session.current_card
        assert card is not None
        print(f"\nПереведите: {card.front}")
        result = session.submit_answer(input("Ваш ответ: "))
        print("Верно!" if result.is_correct else f"Неверно. Правильный ответ: {result.correct_answer}")
    summary = session.summary
    storage.save(trainer)
    print(f"\nРезультат: {summary.correct}/{summary.total}; точность {summary.accuracy_percent:.2f}%")


def _history(trainer: FlashcardTrainer) -> None:
    if not trainer.history:
        print("История сессий пуста")
        return
    for number, summary in enumerate(trainer.history, start=1):
        print(f"Сессия {number}: {summary.correct}/{summary.total}; точность {summary.accuracy_percent:.2f}%")


def run(data_path: str | Path) -> None:
    storage = JsonStorage(data_path)
    trainer = storage.load()
    actions = {
        "1": lambda: _add_card(trainer, storage),
        "2": lambda: _edit_card(trainer, storage),
        "3": lambda: _list_cards(trainer),
        "4": lambda: _study(trainer, storage),
        "5": lambda: _history(trainer),
    }
    while True:
        print("\n=== ФЛЭШ-КАРТЫ: ВАРИАНТ 85 ===")
        print("1 — Создать карточку")
        print("2 — Обновить карточку")
        print("3 — Посмотреть карточки")
        print("4 — Начать учебную сессию")
        print("5 — История и статистика")
        print("0 — Выход")
        try:
            choice = input("Выбор: ").strip()
            if choice == "0":
                print("До встречи!")
                return
            action = actions.get(choice)
            if action is None:
                print("Выберите число от 0 до 5")
                continue
            try:
                action()
            except (ValueError, KeyError, RuntimeError, OSError) as error:
                print(f"Ошибка: {error}")
        except (EOFError, KeyboardInterrupt):
            print("\nЗавершение работы")
            return


def main() -> None:
    parser = argparse.ArgumentParser(description="Практическая работа № 3, вариант 85")
    parser.add_argument("--data", default="flashcards_data.json", help="Путь к JSON-файлу карточек")
    args = parser.parse_args()
    run(args.data)
