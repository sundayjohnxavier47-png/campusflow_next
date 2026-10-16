"""Read-only ticket search with combined filters.

Searching NEVER modifies tickets. All supplied filters must match (logical
AND); an empty filter means "do not filter by that field".

The allowed categories, statuses and priorities come from the modules that own
them (tickets.py and workflow.py), so there is one source of truth.
"""

from campusflow.tickets import ALLOWED_CATEGORIES
from campusflow.workflow import PRIORITY_ORDER, VALID_STATUSES


def parse_category_filter(text):
    """'' (no filter) or a category written exactly as in ALLOWED_CATEGORIES."""
    cleaned = "" if text is None else str(text).strip()
    if not cleaned:
        return ""
    for category in ALLOWED_CATEGORIES:
        if category.casefold() == cleaned.casefold():
            return category
    raise ValueError(f"Invalid category. Choose one of: {', '.join(ALLOWED_CATEGORIES)}.")


def parse_status_filter(text):
    """'' (no filter) or one of open / in_progress / resolved."""
    cleaned = "" if text is None else str(text).strip().casefold()
    if not cleaned:
        return ""
    if cleaned in VALID_STATUSES:
        return cleaned
    raise ValueError(f"Invalid status. Choose one of: {', '.join(VALID_STATUSES)}.")


def parse_priority_filter(text):
    """'' (no filter) or one of critical / high / medium / low."""
    cleaned = "" if text is None else str(text).strip().casefold()
    if not cleaned:
        return ""
    if cleaned in PRIORITY_ORDER:
        return cleaned
    raise ValueError(f"Invalid priority. Choose one of: {', '.join(PRIORITY_ORDER)}.")


def search_tickets(tickets, title_query: str | None ="", category="", status="", priority=""):
    """Return the tickets that match EVERY supplied filter, in original order.

    * title_query: case-insensitive substring of the title (casefold). Only
      the exact text is matched, so 'wi-fi' and 'WI-FI' match each other but
      'wifi' does not match 'Wi-Fi'. No fuzzy matching.
    * category / status / priority: case-insensitive exact match.
    * Blank filters are ignored. An invalid category, status or priority
      raises ValueError.

    The input list and its tickets are never changed.
    """
    title = "" if title_query is None else str(title_query).strip().casefold()
    category = parse_category_filter(category)
    status = parse_status_filter(status)
    priority = parse_priority_filter(priority)

    results = []
    for ticket in tickets:
        if title and title not in str(ticket.get("title", "")).casefold():
            continue
        if category and str(ticket.get("category", "")).strip().casefold() != category.casefold():
            continue
        if status and str(ticket.get("status", "")).strip().casefold() != status:
            continue
        if priority and str(ticket.get("priority", "")).strip().casefold() != priority:
            continue
        results.append(ticket)
    return results


def ticket_number(ticket):
    """The number inside the ID: 'T010' -> 10 (so T9 sorts before T10)."""
    digits = "".join(char for char in str(ticket.get("id", "")) if char.isdigit())
    return int(digits) if digits else 0


def _sort_key(ticket):
    priority = str(ticket.get("priority", "")).strip().lower()
    return PRIORITY_ORDER.get(priority, len(PRIORITY_ORDER)), ticket_number(ticket)


def sort_by_priority(tickets):
    """Return a NEW list sorted critical > high > medium > low, then by ID.

    This is separate from the Open Work Queue: it sorts whatever list it is
    given (for example search results) and does not filter by status.
    """
    return sorted(tickets, key=_sort_key)


def format_result_line(ticket):
    """One display line: ID | title | category | priority | status | assigned_to."""
    assigned = ticket.get("assigned_to") or "unassigned"
    return (
        f"{ticket.get('id')} | {ticket.get('title')} | {ticket.get('category')} | "
        f"{ticket.get('priority')} | {ticket.get('status')} | {assigned}"
    )