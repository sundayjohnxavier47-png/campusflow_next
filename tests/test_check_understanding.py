import tempfile
import unittest
from pathlib import Path

from campusflow.questions import QUESTIONS
from campusflow.check_understanding import (
    DEFAULT_EXPLAIN_IDS,
    ask_question,
    ask_text,
    normalize_choice,
    run_check,
    score_answers,
)

EXPLANATION = "Because the ticket must be assigned first"


class FakeInput:
    """A fake input() that returns the given values in order."""

    def __init__(self, queue):
        self.queue = list(queue)

    def __call__(self, prompt=""):
        if not self.queue:
            raise AssertionError("The quiz asked for more input than the test supplied.")
        return self.queue.pop(0)

    def remaining(self):
        return len(self.queue)


def scripted(values):
    return FakeInput(values)
# Inside your test setup:
# return FakeInput(queue)

def collector():
    """A fake print() that stores every line."""
    lines = []
    return lines, lines.append


def correct_answers():
    return {question["id"]: question["correct"] for question in QUESTIONS}


def wrong_letter(question):
    return next(letter for letter in "ABCD" if letter != question["correct"])


class TestQuestionBank(unittest.TestCase):
    def test_bank_has_six_questions_with_four_options_each(self):
        self.assertEqual(len(QUESTIONS), 6)
        for question in QUESTIONS:
            with self.subTest(question=question["id"]):
                self.assertEqual(sorted(question["options"]), ["A", "B", "C", "D"])
                self.assertIn(question["correct"], question["options"])
                self.assertTrue(question["prompt"].strip())
                self.assertTrue(question["explanation"].strip())

    def test_question_ids_are_unique(self):
        ids = [question["id"] for question in QUESTIONS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_correct_answers_match_the_sprint_guide(self):
        self.assertEqual(
            [question["correct"] for question in QUESTIONS],
            ["B", "C", "B", "C", "C", "B"],
        )


class TestScoring(unittest.TestCase):
    """Acceptance case 14 (scoring half)."""

    def test_all_correct_scores_six(self):
        self.assertEqual(score_answers(QUESTIONS, correct_answers()), 6)

    def test_all_wrong_scores_zero(self):
        answers = {question["id"]: wrong_letter(question) for question in QUESTIONS}
        self.assertEqual(score_answers(QUESTIONS, answers), 0)

    def test_partial_score_counts_one_point_per_correct_answer(self):
        answers = correct_answers()
        for question in QUESTIONS[:3]:
            answers[question["id"]] = wrong_letter(question)
        self.assertEqual(score_answers(QUESTIONS, answers), 3)

    def test_missing_answers_score_nothing(self):
        self.assertEqual(score_answers(QUESTIONS, {"Q1": "B"}), 1)
        self.assertEqual(score_answers(QUESTIONS, {}), 0)

    def test_lowercase_answers_are_accepted(self):
        self.assertEqual(score_answers(QUESTIONS, {"Q1": "b"}), 1)

    def test_scoring_works_with_any_question_bank(self):
        bank = [
            {"id": "X1", "correct": "D"},
            {"id": "X2", "correct": "A"},
        ]
        self.assertEqual(score_answers(bank, {"X1": "D", "X2": "B"}), 1)


class TestChoiceValidation(unittest.TestCase):
    def test_valid_choices_are_normalised(self):
        self.assertEqual(normalize_choice(" b "), "B")
        self.assertEqual(normalize_choice("D"), "D")

    def test_invalid_choices_raise(self):
        for bad in ("E", "", "AB", "1", "  ", None):
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):
                    normalize_choice(bad)

    def test_ask_question_rejects_invalid_answers_then_accepts(self):
        lines, output = collector()
        fake_input = scripted(["E", "", "1", "b"])
        choice = ask_question(QUESTIONS[0], 1, 6, fake_input, output)
        self.assertEqual(choice, "B")
        self.assertEqual(fake_input.remaining(), 0)
        self.assertEqual(sum("A, B, C or D" in line for line in lines), 3)

    def test_ask_question_shows_the_prompt_and_all_options(self):
        lines, output = collector()
        ask_question(QUESTIONS[0], 1, 6, scripted(["A"]), output)
        text = "\n".join(lines)
        self.assertIn("Question 1 of 6", text)
        for letter in "ABCD":
            self.assertIn(f"{letter}. ", text)


class TestAskText(unittest.TestCase):
    def test_short_text_is_asked_again(self):
        lines, output = collector()
        fake_input = scripted(["short", "   ", "This one is long enough"])
        self.assertEqual(ask_text("Why? ", 10, fake_input, output), "This one is long enough")
        self.assertEqual(len(lines), 2)


class TestRunCheck(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.notes_file = Path(self.temp.name) / "notes.md"

    def tearDown(self):
        self.temp.cleanup()

    def all_correct_inputs(self):
        # name, Q1 + explanation, Q2, Q3, Q4, Q5 + explanation, Q6
        return ["Ada", "B", EXPLANATION, "C", "B", "C", "C", EXPLANATION, "B"]

    def test_all_correct_run_scores_six(self):
        lines, output = collector()
        fake_input = scripted(self.all_correct_inputs())
        result = run_check(input_fn=fake_input, output_fn=output, notes_file=self.notes_file)
        self.assertEqual(result["score"], 6)
        self.assertEqual(result["total"], 6)
        self.assertEqual(fake_input.remaining(), 0)
        self.assertIn("Final score: 6/6", "\n".join(lines))

    def test_invalid_answer_is_rejected_and_score_uses_the_submitted_answer(self):
        lines, output = collector()
        inputs = ["Ada", "Z", "x", "A", EXPLANATION,      # Q1: two invalid tries, then A (wrong)
                  "C", "B", "C", "C", EXPLANATION, "B"]
        fake_input = scripted(inputs)
        result = run_check(input_fn=fake_input, output_fn=output, notes_file=self.notes_file)
        self.assertEqual(result["answers"]["Q1"], "A")
        self.assertEqual(result["score"], 5)               # feedback did not change the score
        self.assertEqual(fake_input.remaining(), 0)
        self.assertEqual(sum("A, B, C or D" in line for line in lines), 2)

    def test_all_wrong_run_scores_zero_even_though_feedback_is_shown(self):
        lines, output = collector()
        inputs = ["Ada"]
        for question in QUESTIONS:
            inputs.append(wrong_letter(question))
            if question["id"] in DEFAULT_EXPLAIN_IDS:
                inputs.append(EXPLANATION)
        result = run_check(input_fn=scripted(inputs), output_fn=output, notes_file=self.notes_file)
        self.assertEqual(result["score"], 0)
        self.assertIn("Not quite", "\n".join(lines))

    def test_at_least_two_explanations_are_collected(self):
        self.assertGreaterEqual(len(DEFAULT_EXPLAIN_IDS), 2)
        result = run_check(input_fn=scripted(self.all_correct_inputs()),
                           output_fn=collector()[1], notes_file=self.notes_file)
        self.assertEqual(sorted(result["explanations"]), sorted(DEFAULT_EXPLAIN_IDS))

    def test_a_too_short_explanation_is_asked_again(self):
        inputs = ["Ada", "B", "no", "ok", EXPLANATION, "C", "B", "C", "C", EXPLANATION, "B"]
        fake_input = scripted(inputs)
        result = run_check(input_fn=fake_input, output_fn=collector()[1], notes_file=self.notes_file)
        self.assertEqual(result["explanations"]["Q1"], EXPLANATION)
        self.assertEqual(fake_input.remaining(), 0)

    def test_explanations_never_change_the_score(self):
        weak = ["Ada", "B", "x" * 10, "C", "B", "C", "C", "y" * 10, "B"]
        result = run_check(input_fn=scripted(weak), output_fn=collector()[1],
                           notes_file=self.notes_file)
        self.assertEqual(result["score"], 6)

    def test_learning_note_is_saved_with_score_and_explanations(self):
        run_check(input_fn=scripted(self.all_correct_inputs()),
                  output_fn=collector()[1], notes_file=self.notes_file)
        text = self.notes_file.read_text(encoding="utf-8")
        self.assertIn("Ada", text)
        self.assertIn("Score: 6/6", text)
        self.assertIn(EXPLANATION, text)
        self.assertIn("Q1=B", text)

    def test_running_twice_appends_instead_of_overwriting(self):
        for _ in range(2):
            run_check(input_fn=scripted(self.all_correct_inputs()),
                      output_fn=collector()[1], notes_file=self.notes_file)
        text = self.notes_file.read_text(encoding="utf-8")
        self.assertEqual(text.count("## Ada"), 2)

#     def test_notes_file_none_saves_nothing(self):
#         run_check(input_fn=scripted(self.all_correct_inputs()),
#                   output_fn=collector()[1], notes_file=None)
#         self.assertFalse(self.notes_file.exists())

#     def test_custom_question_bank_works_without_changing_the_logic(self):
#         bank = [{
#             "id": "X1", "prompt": "Pick D", "correct": "D", "explanation": "Because D.",
#             "options": {"A": "a", "B": "b", "C": "c", "D": "d"},
#         }]
#         result = run_check(questions=bank, input_fn=scripted(["Ada", "D"]),
#                            output_fn=collector()[1], explain_ids=(), notes_file=None)
#         self.assertEqual((result["score"], result["total"]), (1, 1))


if __name__ == "__main__":
    unittest.main()