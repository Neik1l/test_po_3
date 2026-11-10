"""SDD: спецификация ожидаемого результата на конкретных примерах."""
import unittest

from flashcards import FlashcardTrainer


class TestSpecificationByExample(unittest.TestCase):
    EXAMPLES = [
        (["кот", "собака"], 2, 0, 100.0),
        (["кот", "ошибка"], 1, 1, 50.0),
        (["ошибка", "ошибка"], 0, 2, 0.0),
        ([" КОТ ", "СОБАКА"], 2, 0, 100.0),
    ]

    def test_results_match_specification_table(self):
        for answers, correct, incorrect, accuracy in self.EXAMPLES:
            with self.subTest(answers=answers):
                trainer = FlashcardTrainer()
                trainer.create_card("cat", "кот")
                trainer.create_card("dog", "собака")
                session = trainer.start_session()
                for answer in answers:
                    session.submit_answer(answer)
                self.assertEqual(session.summary.correct, correct)
                self.assertEqual(session.summary.incorrect, incorrect)
                self.assertEqual(session.summary.accuracy_percent, accuracy)


if __name__ == "__main__":
    unittest.main()
