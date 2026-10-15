import copy
import json
import os

from campusflow.tickets import calculate_priority
from campusflow.validation import (
    validate_affected_users,
    validate_category,
    validate_note_author,
    validate_note_message,
    validate_staff_name,
    validate_status,
    validate_ticket_id,
    validate_title,
    validate_urgency,
)

DEFAULT_PATH = os.path.join("data", "tickets.json")

REQUIRED_TICKET_KEYS = [
    "id", "title", "category", "urgency",
    "affected_users", "priority", "status", "assigned_to",
]
NOTE_KEYS = {"note_id", "author", "message"}


def _check_notes(notes):
    if not isinstance(notes, list):
        raise ValueError("notes must be a list.")

    seen_note_ids = set()
    for note in notes:
        if not isinstance(note, dict) or set(note) != NOTE_KEYS:
            raise ValueError("each note needs exactly note_id, author and message.")

        note_id = note["note_id"]
        if not (
            isinstance(note_id, str)
            and note_id.startswith("N")
            and note_id[1:].isascii()
            and note_id[1:].isdigit()
        ):
            raise ValueError(f"bad note ID {note_id!r}.")
        if note_id in seen_note_ids:
            raise ValueError(f"duplicate note ID {note_id}.")
        seen_note_ids.add(note_id)

        validate_note_author(note["author"])
        validate_note_message(note["message"])


def _check_ticket_fields(ticket):
    ticket_id = validate_ticket_id(ticket["id"])
    if ticket_id != ticket["id"]:
        raise ValueError("ID must look like T001.")

    validate_title(ticket["title"])

    if validate_category(ticket["category"]) != ticket["category"]:
        raise ValueError("category is not in its standard form.")
    if validate_urgency(ticket["urgency"]) != ticket["urgency"]:
        raise ValueError("urgency is not in its standard form.")
    if validate_status(ticket["status"]) != ticket["status"]:
        raise ValueError("status is not in its standard form.")

    validate_affected_users(ticket["affected_users"])

    expected = calculate_priority(ticket["urgency"], ticket["affected_users"])
    if ticket["priority"] != expected:
        raise ValueError(
            f'priority is "{ticket["priority"]}" but urgency and affected '
            f'users give "{expected}".'
        )

    assigned = ticket["assigned_to"]
    if assigned is not None:
        validate_staff_name(assigned)
    if ticket["status"] != "open" and assigned is None:
        raise ValueError("an in_progress or resolved ticket must be assigned.")

    # Old files have no notes. That is allowed: they count as an empty list.
    _check_notes(ticket.get("notes", []))


def validate_ticket_collection(data):
    """Check a whole collection BEFORE it is used.

    Returns a NEW, checked copy of the tickets (old tickets get notes=[]).
    Raises ValueError on the first problem. Never changes `data`.
    """
    if not isinstance(data, list):
        raise ValueError("expected a list of tickets.")

    checked = []
    seen_ids = set()

    for position, ticket in enumerate(data, start=1):
        label = f"ticket #{position}"

        if not isinstance(ticket, dict):
            raise ValueError(f"{label} is not a ticket record.")

        missing = [key for key in REQUIRED_TICKET_KEYS if key not in ticket]
        if missing:
            raise ValueError(f"{label} is missing: {', '.join(missing)}.")

        try:
            _check_ticket_fields(ticket)
        except ValueError as error:
            raise ValueError(f"{label} ({ticket['id']}): {error}")

        if ticket["id"] in seen_ids:
            raise ValueError(f"duplicate ticket ID {ticket['id']}.")
        seen_ids.add(ticket["id"])

        clean = copy.deepcopy(ticket)
        clean.setdefault("notes", [])
        checked.append(clean)

    return checked


def load_tickets(path=DEFAULT_PATH):
    """Return a checked list of tickets, or raise ValueError.

    The caller only replaces its current tickets if this returns, so a
    failed load can never leave memory half-overwritten.
    """
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValueError(f"Ticket file is corrupted: {error}")
    except OSError as error:
        raise ValueError(f"Ticket file could not be read: {error}")

    try:
        return validate_ticket_collection(data)
    except ValueError as error:
        raise ValueError(f"Ticket file is corrupted: {error}")


def save_tickets(tickets, path=DEFAULT_PATH):
    # Never write data that load_tickets would refuse to read back.
    validate_ticket_collection(tickets)

    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)

    temp_path = path + ".tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as file:
            json.dump(tickets, file, indent=2)
        os.replace(temp_path, path)
    finally:
        # If anything failed, do not leave a half-written temp file behind.
        if os.path.exists(temp_path):
            os.remove(temp_path)