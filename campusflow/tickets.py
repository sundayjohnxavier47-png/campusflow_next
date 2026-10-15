from campusflow.validation import (
    ALLOWED_CATEGORIES,  # re-exported so old imports keep working
    ALLOWED_URGENCY,
    validate_affected_users,
    validate_category,
    validate_title,
    validate_urgency,
)


def calculate_priority(urgency, affected_users):
    if urgency == "high" and affected_users >= 10:
        return "critical"
    elif urgency == "high" or affected_users >= 10:
        return "high"
    elif urgency == "medium" or affected_users >= 3:
        return "medium"
    else:
        return "low"


def create_ticket(tickets, title, category, urgency, affected_users):
    # Validate EVERYTHING first. Nothing is changed until all checks pass.
    title = validate_title(title)
    category = validate_category(category)
    urgency = validate_urgency(urgency)
    affected_users = validate_affected_users(affected_users)

    numbers = [
        int(ticket["id"][1:])
        for ticket in tickets
        if isinstance(ticket.get("id"), str)
        and ticket["id"].startswith("T")
        and ticket["id"][1:].isdigit()
    ]

    next_number = max(numbers, default=0) + 1
    ticket_id = f"T{next_number:03d}"

    priority = calculate_priority(urgency, affected_users)

    ticket = {
        "id": ticket_id,
        "title": title,
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": priority,
        "status": "open",
        "assigned_to": None,
        "notes": [],
    }

    tickets.append(ticket)
    return ticket