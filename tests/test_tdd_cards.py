"""TDD: тесты карточек пишутся раньше реализации; RED → GREEN → REFACTOR."""
import unittest

from flashcards import FlashcardTrainer


class TestCardTDD(unittest.TestCase):
    def setUp(self):
        self.trainer = FlashcardTrainer()

    def test_create_card_returns_expected_fields(self):
        card = self.trainer.create_card("cat", "кот")
        self.assertEqual((card.id, card.front, card.back), (1, "cat", "кот"))

    def test_card_ids_are_unique_and_incremental(self):
        first = self.trainer.create_card("cat", "кот")
        second = self.trainer.create_card("dog", "собака")
        self.assertEqual((first.id, second.id), (1, 2))

    def test_creating_blank_front_is_rejected(self):
        with self.assertRaises(ValueError):
            self.trainer.create_card("  ", "кот")
        self.assertEqual(self.trainer.list_cards(), [])

    def test_creating_blank_back_is_rejected(self):
        with self.assertRaises(ValueError):
            self.trainer.create_card("cat", " ")

    def test_fields_trim_leading_and_trailing_spaces(self):
        card = self.trainer.create_card(" cat ", " кот ", " Английский ")
        self.assertEqual((card.front, card.back, card.language), ("cat", "кот", "Английский"))

    def test_update_card_changes_only_requested_field(self):
        original = self.trainer.create_card("cat", "кот", "Английский")
        updated = self.trainer.update_card(original.id, back="кошка")
        self.assertEqual((updated.front, updated.back, updated.language), ("cat", "кошка", "Английский"))

    def test_updating_unknown_card_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.trainer.update_card(999, back="нет")

    def test_invalid_update_does_not_modify_original(self):
        original = self.trainer.create_card("cat", "кот")
        with self.assertRaises(ValueError):
            self.trainer.update_card(original.id, front="")
        self.assertEqual(self.trainer.get_card(original.id), original)

    def test_cards_are_listed_in_creation_order(self):
        self.trainer.create_card("cat", "кот")
        self.trainer.create_card("dog", "собака")
        self.assertEqual([card.front for card in self.trainer.list_cards()], ["cat", "dog"])


if __name__ == "__main__":
    unittest.main()
