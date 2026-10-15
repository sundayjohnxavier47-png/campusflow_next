
ALLOWED_CATEGORIES = ["Network", "Hardware", "Software", "Other"]
ALLOWED_URGENCY = ["low", "medium", "high"]


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
    
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Title cannot be blank.")

    
    if not isinstance(category, str):
        raise ValueError("Invalid category.")

    category = category.strip().title()

    if category not in ALLOWED_CATEGORIES:
        raise ValueError("Category must be Network, Hardware, Software, or Other.")

    
    if not isinstance(urgency, str):
        raise ValueError("Invalid urgency.")

    urgency = urgency.strip().lower()

    if urgency not in ALLOWED_URGENCY:
        raise ValueError("Urgency must be low, medium, or high.")

    
    if type(affected_users) is not int or affected_users <= 0:
        raise ValueError("Affected users must be a positive integer.")

    
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
        "title": title.strip(),
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": priority,
        "status": "open",
        "assigned_to": None
    }

    tickets.append(ticket)

    return ticket
