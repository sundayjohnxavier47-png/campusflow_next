VALID_STATUSES = ["open", "in_progress", "resolved"]

ALLOWED_TRANSITIONS = {
    "open": ["in_progress"],
    "in_progress": ["resolved"],
    "resolved": [],
}

PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def find_ticket(tickets, ticket_id):
    if not isinstance(ticket_id, str):
        raise ValueError("Ticket ID must be text.")

    ticket_id = ticket_id.strip().upper()

    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket

    raise ValueError(f"Ticket {ticket_id} was not found.")


def assign_ticket(tickets, ticket_id, staff_name):
    ticket = find_ticket(tickets, ticket_id)

    if not isinstance(staff_name, str) or not staff_name.strip():
        raise ValueError("Staff name cannot be blank.")

    if ticket["status"] == "resolved":
        raise ValueError("Resolved tickets must be reopened before changes.")

    ticket["assigned_to"] = staff_name.strip()
    return ticket


def change_status(tickets, ticket_id, new_status):
    ticket = find_ticket(tickets, ticket_id)

    if not isinstance(new_status, str):
        raise ValueError("Status must be text.")

    new_status = new_status.strip().lower()

    if new_status not in VALID_STATUSES:
        raise ValueError("Status must be open, in_progress, or resolved.")

    current = ticket["status"]

    if current == "resolved":
        raise ValueError("Resolved tickets must be reopened first.")

    if new_status not in ALLOWED_TRANSITIONS[current]:
        raise ValueError(f"Cannot move from {current} to {new_status}.")

    if new_status == "in_progress" and not ticket["assigned_to"]:
        raise ValueError("Assign the ticket before moving it to in_progress.")

    ticket["status"] = new_status
    return ticket


def reopen_ticket(tickets, ticket_id):
    ticket = find_ticket(tickets, ticket_id)

    if ticket["status"] != "resolved":
        raise ValueError("Only resolved tickets can be reopened.")

    ticket["status"] = "open"
    return ticket


def get_work_queue(tickets):
    open_tickets = [t for t in tickets if t["status"] == "open"]

    return sorted(
        open_tickets,
        key=lambda t: (PRIORITY_ORDER[t["priority"]], int(t["id"][1:])),
    )