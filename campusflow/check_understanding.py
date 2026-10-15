"""Engineering Understanding Check: scoring logic and the interactive quiz.

The question bank is in questions.py. Input and output functions are passed in
(defaulting to input and print) so every part can be tested without typing.

Rules:
  * Answers must be A, B, C or D; anything else is asked again.
  * One point per correct SUBMITTED answer. Feedback after each question never
    changes the score.
  * Explanations are only recorded for mentor discussion. They are never
    auto-graded and never affect the score.
"""

from datetime import datetime
from pathlib import Path

from campusflow.questions import QUESTIONS

VALID_CHOICES = ("A", "B", "C", "D")
DEFAULT_EXPLAIN_IDS = ("Q1", "Q5")
MIN_EXPLANATION_LENGTH = 10

NOTES_FILE = Path(__file__).resolve().parent.parent / "docs" / "understanding-check-notes.md"


def _io(input_fn, output_fn):
    """Resolve input/print when called, not when the module is imported.

    Default arguments such as input_fn=input would capture the real input()
    function at import time and ignore anything substituted later.
    """
    return (input if input_fn is None else input_fn), (print if output_fn is None else output_fn)


def normalize_choice(text):
    """' b ' -> 'B'. Raises ValueError unless the answer is A, B, C or D."""
    cleaned = str(text).strip().upper()
    if cleaned not in VALID_CHOICES:
        raise ValueError("Please answer with A, B, C or D.")
    return cleaned


def score_answers(questions, answers):
    """Count correct answers.

    answers maps question id -> choice letter. A missing or invalid answer
    scores nothing. The question bank is a parameter, so no question or
    correct answer is hard-coded here.
    """
    score = 0
    for question in questions:
        try:
            choice = normalize_choice(answers.get(question["id"], ""))
        except ValueError:
            continue
        if choice == question["correct"]:
            score += 1
    return score


def ask_question(question, number, total, input_fn=None, output_fn=None):
    """Show one question and keep asking until the answer is A, B, C or D."""
    input_fn, output_fn = _io(input_fn, output_fn)
    output_fn(f"\nQuestion {number} of {total}: {question['prompt']}")
    for letter in VALID_CHOICES:
        output_fn(f"  {letter}. {question['options'][letter]}")
    while True:
        try:
            return normalize_choice(input_fn("Your answer (A/B/C/D): "))
        except ValueError as error:
            output_fn(f"  {error}")


def ask_text(prompt, min_length, input_fn=None, output_fn=None):
    """Ask until the trimmed answer has at least min_length characters."""
    input_fn, output_fn = _io(input_fn, output_fn)
    while True:
        text = str(input_fn(prompt)).strip()
        if len(text) >= min_length:
            return text
        output_fn(f"  Please write at least {min_length} characters.")


def format_learning_note(result):
    lines = [
        f"## {result['learner']} - {result['date']}",
        f"Score: {result['score']}/{result['total']}",
        "Answers: " + ", ".join(f"{qid}={choice}" for qid, choice in result["answers"].items()),
        "",
        "Explanations (for mentor discussion, not auto-graded):",
    ]
    for qid, text in result["explanations"].items():
        lines.append(f"- {qid} (chose {result['answers'][qid]}): {text}")
    lines.append("")
    return "\n".join(lines) + "\n"


def save_learning_note(result, filename=NOTES_FILE):
    """Append the result and explanations to the learning-note file."""
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as file:
        file.write(format_learning_note(result))


def run_check(
    questions=QUESTIONS,
    input_fn=None,
    output_fn=None,
    explain_ids=DEFAULT_EXPLAIN_IDS,
    notes_file=NOTES_FILE,
):
    """Run the quiz and return a result dictionary.

    Order of prompts: learner name; then for each question the answer, the
    feedback, and (only for ids in explain_ids) a written explanation.
    Pass notes_file=None to skip saving the learning note.
    """
    input_fn, output_fn = _io(input_fn, output_fn)
    output_fn("------ Engineering Understanding Check ------")
    learner = ask_text("Your name: ", 1, input_fn, output_fn)

    total = len(questions)
    answers = {}
    explanations = {}

    for number, question in enumerate(questions, start=1):
        choice = ask_question(question, number, total, input_fn, output_fn)
        answers[question["id"]] = choice

        if choice == question["correct"]:
            output_fn("  Correct.")
        else:
            correct = question["correct"]
            output_fn(f"  Not quite. The correct answer is {correct}: {question['options'][correct]}")
        output_fn(f"  Why: {question['explanation']}")

        if question["id"] in explain_ids:
            explanations[question["id"]] = ask_text(
                f"Explain in your own words why you chose {choice} "
                f"(at least {MIN_EXPLANATION_LENGTH} characters): ",
                MIN_EXPLANATION_LENGTH,
                input_fn,
                output_fn,
            )

    score = score_answers(questions, answers)
    output_fn(f"\nFinal score: {score}/{total}")

    result = {
        "learner": learner,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "score": score,
        "total": total,
        "answers": answers,
        "explanations": explanations,
    }

    if explanations:
        output_fn("\nYour explanations (for mentor discussion):")
        for qid, text in explanations.items():
            output_fn(f"  {qid}: {text}")

    if notes_file is not None:
        try:
            save_learning_note(result, notes_file)
            output_fn(f"Learning note saved to {notes_file}")
        except OSError as error:
            output_fn(f"Could not save the learning note: {error}")

    return result