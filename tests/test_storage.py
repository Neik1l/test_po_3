"""Проверка записи/чтения JSON и реакции на повреждённый файл."""
import json
import tempfile
import unittest
from pathlib import Path

from flashcards.storage import JsonStorage


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.storage = JsonStorage(Path(self.temp.name) / "cards.json")

    def test_missing_file_creates_empty_collection(self):
        self.assertEqual(self.storage.load().list_cards(), [])

    def test_roundtrip_restores_cards_and_history(self):
        trainer = self.storage.load()
        trainer.create_card("cat", "кот")
        session = trainer.start_session()
        session.submit_answer("кот")
        self.storage.save(trainer)
        restored = self.storage.load()
        self.assertEqual(restored.get_card(1).back, "кот")
        self.assertEqual(restored.history[0].accuracy_percent, 100)
        self.assertEqual(restored.create_card("dog", "собака").id, 2)

    def test_corrupted_json_is_rejected(self):
        self.storage.path.write_text("{this is not json", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.storage.load()

    def test_duplicate_ids_in_stored_data_are_rejected(self):
        card = {"id": 1, "front": "cat", "back": "кот", "language": "Английский"}
        self.storage.path.write_text(json.dumps({"cards": [card, card]}), encoding="utf-8")
        with self.assertRaises(ValueError):
            self.storage.load()


if __name__ == "__main__":
    unittest.main()
