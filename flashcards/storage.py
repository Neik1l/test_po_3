"""Хранение карточек и истории занятий на локальном диске."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from .trainer import FlashcardTrainer


class JsonStorage:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self) -> FlashcardTrainer:
        if not self.path.exists():
            return FlashcardTrainer()
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise ValueError("Файл данных повреждён или имеет неверную кодировку") from error
        return FlashcardTrainer.from_dict(raw)

    def save(self, trainer: FlashcardTrainer) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", dir=self.path.parent,
                prefix=".flashcards_", suffix=".tmp", delete=False
            ) as file:
                temp_path = Path(file.name)
                json.dump(trainer.to_dict(), file, ensure_ascii=False, indent=2)
                file.write("\n")
            os.replace(temp_path, self.path)
        finally:
            if temp_path is not None and temp_path.exists():
                temp_path.unlink()
