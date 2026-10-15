"""Question bank for the Engineering Understanding Check.

This file holds DATA ONLY. Scoring and the menu loop live in
understanding_check.py, so questions can change without touching the logic.
"""

QUESTIONS = [
    {
        "id": "Q1",
        "prompt": (
            "Ticket T001 is open and unassigned. A user tries to move it to "
            "in_progress. What should happen?"
        ),
        "options": {
            "A": "Accept",
            "B": "Reject and preserve all data",
            "C": "Resolve it automatically",
            "D": "Remove ticket",
        },
        "correct": "B",
        "explanation": (
            "An unassigned ticket cannot start work. The action is rejected "
            "with an error and the ticket collection stays exactly as it was."
        ),
    },
    {
        "id": "Q2",
        "prompt": "The app has zero tickets. What should the resolution percentage display?",
        "options": {
            "A": "Crash",
            "B": "100%",
            "C": "0%",
            "D": "Divide by one without explanation",
        },
        "correct": "C",
        "explanation": (
            "resolved / total would divide by zero, so an empty dataset is "
            "handled as a special case and reports 0%."
        ),
    },
    {
        "id": "Q3",
        "prompt": "Filter title='wifi', category='Network', status='open'. Which records should match?",
        "options": {
            "A": "Any record matching one filter",
            "B": "Only records matching all supplied filters",
            "C": "All network records",
            "D": "All open records",
        },
        "correct": "B",
        "explanation": (
            "Filters combine with logical AND: a ticket must satisfy every "
            "filter that was supplied."
        ),
    },
    {
        "id": "Q4",
        "prompt": "A resolved ticket receives 'Add note'. What should happen?",
        "options": {
            "A": "Append anyway",
            "B": "Delete old notes",
            "C": "Reject until reopened",
            "D": "Change status silently",
        },
        "correct": "C",
        "explanation": (
            "Only open or in_progress tickets accept notes. A resolved ticket "
            "must be reopened through the normal workflow first."
        ),
    },
    {
        "id": "Q5",
        "prompt": "The JSON file includes two tickets with the same ID. What should load do?",
        "options": {
            "A": "Keep both",
            "B": "Replace memory with duplicates",
            "C": "Reject the load without changing current memory",
            "D": "Rename IDs silently",
        },
        "correct": "C",
        "explanation": (
            "The whole file is validated before anything replaces memory. "
            "Duplicate IDs make the file invalid, so the load is rejected."
        ),
    },
    {
        "id": "Q6",
        "prompt": "A PR changes validation but has no negative-case tests. What is the best review action?",
        "options": {
            "A": "Approve because it runs",
            "B": "Request focused tests and reasoning",
            "C": "Merge immediately",
            "D": "Ask AI to approve it",
        },
        "correct": "B",
        "explanation": (
            "Code that runs is not proof it rejects bad input. A good review "
            "names the missing cases and asks for tests that prove them."
        ),
    },
]