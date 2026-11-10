"""Модульные тесты сессий обучения и расчёта статистики."""
import unittest

from flashcards import FlashcardTrainer


class TestSession(unittest.TestCase):
    def setUp(self):
        self.trainer = FlashcardTrainer()
        self.trainer.create_card("cat", "кот")
        self.trainer.create_card("dog", "собака")

    def test_session_moves_from_first_card_to_second(self):
        session = self.trainer.start_session()
        self.assertEqual(session.current_card.front, "cat")
        session.submit_answer("кот")
        self.assertEqual(session.current_card.front, "dog")

    def test_correct_and_incorrect_answers_counted(self):
        session = self.trainer.start_session()
        session.submit_answer("кот")
        session.submit_answer("ошибка")
        self.assertEqual((session.summary.correct, session.summary.incorrect), (1, 1))
        self.assertEqual(session.summary.accuracy_percent, 50.0)

    def test_answer_comparison_ignores_case_and_outer_spaces(self):
        session = self.trainer.start_session([1])
        self.assertTrue(session.submit_answer("  КОТ ").is_correct)

    def test_session_does_not_accept_answers_after_completion(self):
        session = self.trainer.start_session([1])
        session.submit_answer("кот")
        self.assertTrue(session.is_finished)
        self.assertIsNone(session.current_card)
        with self.assertRaises(RuntimeError):
            session.submit_answer("кот")

    def test_history_is_recorded_only_after_all_answers(self):
        session = self.trainer.start_session()
        self.assertEqual(len(self.trainer.history), 0)
        session.submit_answer("кот")
        self.assertEqual(len(self.trainer.history), 0)
        session.submit_answer("собака")
        self.assertEqual(len(self.trainer.history), 1)

    def test_start_session_without_cards_is_rejected(self):
        with self.assertRaises(ValueError):
            FlashcardTrainer().start_session()

    def test_duplicate_card_ids_are_rejected(self):
        with self.assertRaises(ValueError):
            self.trainer.start_session([1, 1])

    def test_session_accuracy_rounds_to_two_decimals(self):
        self.trainer.create_card("sun", "солнце")
        session = self.trainer.start_session()
        session.submit_answer("кот")
        session.submit_answer("ошибка")
        session.submit_answer("ошибка")
        self.assertEqual(session.summary.accuracy_percent, 33.33)


if __name__ == "__main__":
    unittest.main()
