from campusflow.validation import (
    VALID_STATUSES,  # re-exported so old imports keep working
    validate_staff_name,
    validate_status,
    validate_ticket_id,
)

ALLOWED_TRANSITIONS = {
    "open": ["in_progress"],
    "in_progress": ["resolved"],
    "resolved": [],
}

PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def find_ticket(tickets, ticket_id):
    ticket_id = validate_ticket_id(ticket_id)

    for ticket in tickets:
        if ticket.get("id") == ticket_id:
            return ticket

    raise ValueError(f"Ticket {ticket_id} was not found.")


def assign_ticket(tickets, ticket_id, staff_name):
    ticket = find_ticket(tickets, ticket_id)
    staff_name = validate_staff_name(staff_name)

    if ticket["status"] == "resolved":
        raise ValueError("Resolved tickets must be reopened before changes.")

    ticket["assigned_to"] = staff_name
    return ticket


def change_status(tickets, ticket_id, new_status):
    ticket = find_ticket(tickets, ticket_id)
    new_status = validate_status(new_status)

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