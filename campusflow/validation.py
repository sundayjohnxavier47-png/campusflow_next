"""Central validation helpers for CampusFlow.

Each validator checks ONE value. If the value is valid it returns the
cleaned value; if not, it raises ValueError with a friendly message.
Nothing here changes any ticket data.
"""

ALLOWED_CATEGORIES = ["Network", "Hardware", "Software", "Other"]
ALLOWED_URGENCY = ["low", "medium", "high"]
VALID_STATUSES = ["open", "in_progress", "resolved"]

NOTE_MIN_LENGTH = 5
NOTE_MAX_LENGTH = 300


def validate_title(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Title cannot be blank.")
    return value.strip()


def validate_category(value):
    if not isinstance(value, str):
        raise ValueError("Invalid category.")
    cleaned = value.strip().title()
    if cleaned not in ALLOWED_CATEGORIES:
        raise ValueError("Category must be Network, Hardware, Software, or Other.")
    return cleaned


def validate_urgency(value):
    if not isinstance(value, str):
        raise ValueError("Invalid urgency.")
    cleaned = value.strip().lower()
    if cleaned not in ALLOWED_URGENCY:
        raise ValueError("Urgency must be low, medium, or high.")
    return cleaned


def validate_affected_users(value):
    # type(...) is int also rejects True/False, which Python treats as ints.
    if type(value) is not int or value <= 0:
        raise ValueError("Affected users must be a positive integer.")
    return value


def parse_affected_users(text):
    """For typed input: turn text like ' 12 ' into the integer 12."""
    if not isinstance(text, str):
        raise ValueError("Affected users must be a positive whole number.")
    cleaned = text.strip()
    if not (cleaned.isascii() and cleaned.isdigit()):
        raise ValueError("Affected users must be a positive whole number.")
    return validate_affected_users(int(cleaned))


def validate_staff_name(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Staff name cannot be blank.")
    return value.strip()


def validate_ticket_id(value):
    if not isinstance(value, str):
        raise ValueError("Ticket ID must be text.")
    cleaned = value.strip().upper()
    digits = cleaned[1:]
    if not (cleaned.startswith("T") and digits.isascii() and digits.isdigit()):
        raise ValueError("Ticket ID must look like T001.")
    return cleaned


def validate_status(value):
    if not isinstance(value, str):
        raise ValueError("Status must be text.")
    cleaned = value.strip().lower()
    if cleaned not in VALID_STATUSES:
        raise ValueError("Status must be open, in_progress, or resolved.")
    return cleaned


def validate_note_author(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Author cannot be blank.")
    return value.strip()


def validate_note_message(value):
    if not isinstance(value, str):
        raise ValueError("Note message must be text.")
    cleaned = value.strip()
    if not NOTE_MIN_LENGTH <= len(cleaned) <= NOTE_MAX_LENGTH:
        raise ValueError(
            f"Note message must be {NOTE_MIN_LENGTH} to {NOTE_MAX_LENGTH} "
            "characters long."
        )
    return cleaned