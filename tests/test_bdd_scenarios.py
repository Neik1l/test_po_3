"""BDD: минимальный встроенный исполнитель шагов Gherkin (Given/When/Then/And).

Это ограниченный учебный интерпретатор конкретных сценариев в features/study.feature,
а не полная реализация стандарта Gherkin или внешнего фреймворка Behave.
"""
import re
import unittest
from pathlib import Path

from flashcards import FlashcardTrainer

FEATURE_FILE = Path(__file__).resolve().parents[1] / "features" / "study.feature"


def parse_scenarios(text: str) -> list[tuple[str, list[tuple[str, str]]]]:
    scenarios: list[tuple[str, list[tuple[str, str]]]] = []
    current_name = None
    steps = []
    previous_keyword = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("Feature:") or line.startswith("Для") or line.startswith("учащийся"):
            continue
        if line.startswith("Scenario:"):
            if current_name is not None:
                scenarios.append((current_name, steps))
            current_name = line.partition(":")[2].strip()
            steps = []
            previous_keyword = None
            continue
        match = re.fullmatch(r"(Given|When|Then|And)\s+(.+)", line)
        if match is None:
            raise ValueError(f"Неизвестная строка сценария: {line}")
        if current_name is None:
            raise ValueError("Шаг встречен до сценария")
        keyword = match.group(1)
        if keyword == "And":
            if previous_keyword is None:
                raise ValueError("And без предшествующего шага")
            keyword = previous_keyword
        previous_keyword = keyword
        steps.append((keyword, match.group(2)))
    if current_name is not None:
        scenarios.append((current_name, steps))
    return scenarios


class TestGherkinScenarios(unittest.TestCase):
    def _run_scenario(self, steps):
        trainer = FlashcardTrainer()
        session = None
        for kind, statement in steps:
            if kind == "Given":
                match = re.fullmatch(r'созданы карточки "([^"]+)"', statement)
                self.assertIsNotNone(match, statement)
                for token in match.group(1).split(";"):
                    front, back = token.split("=", 1)
                    trainer.create_card(front, back)
            elif kind == "When":
                match = re.fullmatch(r'прохожу сессию с ответами "([^"]+)"', statement)
                self.assertIsNotNone(match, statement)
                session = trainer.start_session()
                for answer in match.group(1).split(";"):
                    session.submit_answer(answer)
            elif kind == "Then":
                if statement.startswith("статистика показывает"):
                    match = re.fullmatch(r"статистика показывает всего (\d+), верных (\d+), точность (\d+)%", statement)
                    self.assertIsNotNone(match, statement)
                    self.assertIsNotNone(session)
                    total, correct, accuracy = (int(x) for x in match.groups())
                    self.assertEqual((session.summary.total, session.summary.correct, session.summary.accuracy_percent),
                                     (total, correct, accuracy))
                elif statement.startswith("история содержит"):
                    match = re.fullmatch(r"история содержит (\d+) сессию", statement)
                    self.assertIsNotNone(match, statement)
                    self.assertEqual(len(trainer.history), int(match.group(1)))
                else:
                    self.fail(f"Неизвестный Then: {statement}")
            else:
                self.fail(f"Неизвестный тип шага: {kind}")

    def test_feature_file_all_scenarios_pass(self):
        scenarios = parse_scenarios(FEATURE_FILE.read_text(encoding="utf-8"))
        self.assertEqual(len(scenarios), 3, "В спецификации должно быть три сценария")
        for name, steps in scenarios:
            with self.subTest(scenario=name):
                self._run_scenario(steps)


if __name__ == "__main__":
    unittest.main()
