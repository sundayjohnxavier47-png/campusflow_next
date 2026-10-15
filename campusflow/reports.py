"""Ticket reports for the Head of Campus.

generate_report keeps the name and the keys the original main.py already uses
(total, by_status, by_priority) and adds category counts, unresolved and
resolved counts and the resolution percentage.

Every ticket is counted once, by its CURRENT status, priority and category.
Values are matched case-insensitively; unknown or missing values count toward
the total but not toward any breakdown, so nothing is double-counted and a
slightly broken record cannot crash the report.
"""

from campusflow.tickets import ALLOWED_CATEGORIES
from campusflow.workflow import PRIORITY_ORDER, VALID_STATUSES


def generate_report(tickets):
    """Return a dictionary of counts. Never modifies the tickets.

    Keys: total, by_status, by_priority, by_category, unresolved (open +
    in_progress), resolved, resolution_percentage (resolved / total * 100,
    which is 0.0 when there are no tickets).
    """
    by_status = {status: 0 for status in VALID_STATUSES}
    by_priority = {priority: 0 for priority in PRIORITY_ORDER}
    by_category = {category: 0 for category in ALLOWED_CATEGORIES}

    for ticket in tickets:
        status = str(ticket.get("status", "")).strip().lower()
        priority = str(ticket.get("priority", "")).strip().lower()
        category = str(ticket.get("category", "")).strip().casefold()

        if status in by_status:
            by_status[status] += 1
        if priority in by_priority:
            by_priority[priority] += 1
        for name in by_category:
            if name.casefold() == category:
                by_category[name] += 1

    total = len(tickets)
    resolved = by_status["resolved"]
    unresolved = by_status["open"] + by_status["in_progress"]

    if total == 0:
        resolution_percentage = 0.0          # avoid dividing by zero
    else:
        resolution_percentage = round(resolved / total * 100, 2)

    return {
        "total": total,
        "by_status": by_status,
        "by_priority": by_priority,
        "by_category": by_category,
        "unresolved": unresolved,
        "resolved": resolved,
        "resolution_percentage": resolution_percentage,
    }


def format_report(report):
    """Turn the dictionary from generate_report into printable text."""
    lines = [f"Total tickets: {report['total']}", "By status:"]
    for status, count in report["by_status"].items():
        lines.append(f"  {status}: {count}")
    lines.append("By priority:")
    for priority, count in report["by_priority"].items():
        lines.append(f"  {priority}: {count}")
    lines.append("By category:")
    for category, count in report["by_category"].items():
        lines.append(f"  {category}: {count}")
    lines.append(f"Unresolved (open + in_progress): {report['unresolved']}")
    lines.append(f"Resolved: {report['resolved']}")
    lines.append(f"Resolution rate: {report['resolution_percentage']:g}%")
    return "\n".join(lines)