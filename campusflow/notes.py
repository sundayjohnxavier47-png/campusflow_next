"""Follow-up notes for tickets.

Error convention (same as the rest of CampusFlow): invalid actions raise
ValueError with a friendly message. Validation always happens BEFORE any
change, so a rejected action leaves the tickets untouched.
"""

from campusflow.validation import validate_note_author, validate_note_message
from campusflow.workflow import find_ticket

NOTE_ALLOWED_STATUSES = ["open", "in_progress"]


def _note_number(note):
    """Return the number in a note ID like 'N003', or None if malformed."""
    note_id = note.get("note_id") if isinstance(note, dict) else None
    if (
        isinstance(note_id, str)
        and note_id.startswith("N")
        and note_id[1:].isascii()
        and note_id[1:].isdigit()
    ):
        return int(note_id[1:])
    return None


def next_note_id(ticket):
    """Return the next free note ID for this ticket (N001, N002, ...).

    The ID is worked out from the notes the ticket already has, so it stays
    correct after saving and reloading, and it never changes any data.
    """
    numbers = [
        number
        for number in (_note_number(note) for note in ticket.get("notes", []))
        if number is not None
    ]
    return f"N{max(numbers, default=0) + 1:03d}"


def add_note(tickets, ticket_id, author, message):
    """Add a follow-up note to a ticket and return the new note.

    Contract:
      Before: the ticket exists and is open or in_progress; author is not
              blank; message is 5-300 characters after trimming.
      After:  the ticket has exactly one more note, with the next note ID.
      Fails:  raises ValueError. When it fails, nothing has changed and no
              note ID has been used.
    """
    ticket = find_ticket(tickets, ticket_id)

    if ticket["status"] not in NOTE_ALLOWED_STATUSES:
        raise ValueError(
            "Notes can only be added to open or in_progress tickets. "
            "Reopen the ticket first."
        )

    author = validate_note_author(author)
    message = validate_note_message(message)

    # Every check has passed. Only now do we change anything.
    note = {
        "note_id": next_note_id(ticket),
        "author": author,
        "message": message,
    }
    ticket.setdefault("notes", []).append(note)
    return note


def get_notes(tickets, ticket_id):
    """Return a ticket's notes in note ID order (read-only)."""
    ticket = find_ticket(tickets, ticket_id)
    notes = ticket.get("notes", [])
    return sorted(
        notes,
        key=lambda note: (_note_number(note) is None, _note_number(note) or 0),
    )