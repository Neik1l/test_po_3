"""ATDD: приемочные критерии пользователя для законченной учебной сессии."""
import unittest

from flashcards import FlashcardTrainer


class TestAcceptanceCriteria(unittest.TestCase):
    def test_user_adds_cards_and_sees_them_in_collection(self):
        trainer = FlashcardTrainer()
        trainer.create_card("book", "книга")
        self.assertEqual(len(trainer.list_cards()), 1)
        self.assertEqual(trainer.list_cards()[0].front, "book")

    def test_learner_finishes_session_and_sees_progress(self):
        trainer = FlashcardTrainer()
        trainer.create_card("cat", "кот")
        trainer.create_card("dog", "собака")
        session = trainer.start_session()
        session.submit_answer("кот")
        session.submit_answer("собака")
        self.assertTrue(session.is_finished)
        self.assertEqual(session.summary.correct, 2)
        self.assertEqual(session.summary.accuracy_percent, 100.0)
        self.assertEqual(trainer.history[0], session.summary)

    def test_wrong_answer_does_not_increase_correct_count(self):
        trainer = FlashcardTrainer()
        trainer.create_card("cat", "кот")
        session = trainer.start_session()
        result = session.submit_answer("собака")
        self.assertFalse(result.is_correct)
        self.assertEqual(session.summary.correct, 0)
        self.assertEqual(session.summary.accuracy_percent, 0)


if __name__ == "__main__":
    unittest.main()
