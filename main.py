from campusflow.tickets import create_ticket
from campusflow.workflow import (
    assign_ticket,
    change_status,
    find_ticket,
    get_work_queue,
    reopen_ticket,
)
from campusflow.reports import generate_report
from campusflow.storage import load_tickets, save_tickets

MENU = """
===== CampusFlow =====
1. Create ticket
2. List all tickets
3. View one ticket
4. Assign ticket
5. Change status
6. Reopen ticket
7. Work queue
8. Report
9. Exit
"""


def show_ticket(ticket):
    assigned = ticket["assigned_to"] or "unassigned"
    print(
        f'{ticket["id"]} | {ticket["title"]} | {ticket["category"]} | '
        f'urgency: {ticket["urgency"]} | users: {ticket["affected_users"]} | '
        f'priority: {ticket["priority"]} | status: {ticket["status"]} | {assigned}'
    )


def handle_create(tickets):
    title = input("Title: ")
    category = input("Category (Network/Hardware/Software/Other): ")
    urgency = input("Urgency (low/medium/high): ")
    users_text = input("Affected users: ")

    try:
        affected_users = int(users_text)
    except ValueError:
        affected_users = users_text  # create_ticket will reject it clearly

    ticket = create_ticket(tickets, title, category, urgency, affected_users)
    save_tickets(tickets)
    print("Created:")
    show_ticket(ticket)


def handle_list(tickets):
    if not tickets:
        print("No tickets yet.")
        return
    for ticket in tickets:
        show_ticket(ticket)


def handle_view(tickets):
    show_ticket(find_ticket(tickets, input("Ticket ID: ")))


def handle_assign(tickets):
    ticket_id = input("Ticket ID: ")
    staff = input("Staff member name: ")
    ticket = assign_ticket(tickets, ticket_id, staff)
    save_tickets(tickets)
    print("Assigned:")
    show_ticket(ticket)


def handle_status(tickets):
    ticket_id = input("Ticket ID: ")
    new_status = input("New status (in_progress/resolved): ")
    ticket = change_status(tickets, ticket_id, new_status)
    save_tickets(tickets)
    print("Updated:")
    show_ticket(ticket)


def handle_reopen(tickets):
    ticket = reopen_ticket(tickets, input("Ticket ID: "))
    save_tickets(tickets)
    print("Reopened:")
    show_ticket(ticket)


def handle_queue(tickets):
    queue = get_work_queue(tickets)
    if not queue:
        print("The work queue is empty.")
        return
    for ticket in queue:
        show_ticket(ticket)


def handle_report(tickets):
    report = generate_report(tickets)
    print(f'Total tickets: {report["total"]}')
    print("By status:")
    for status, count in report["by_status"].items():
        print(f"  {status}: {count}")
    print("By priority:")
    for priority, count in report["by_priority"].items():
        print(f"  {priority}: {count}")


ACTIONS = {
    "1": handle_create,
    "2": handle_list,
    "3": handle_view,
    "4": handle_assign,
    "5": handle_status,
    "6": handle_reopen,
    "7": handle_queue,
    "8": handle_report,
}


def main():
    try:
        tickets = load_tickets()
    except ValueError as error:
        print(f"Error: {error}")
        print("Fix or remove data/tickets.json yourself. Nothing was changed.")
        return

    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()

        if choice == "9":
            print("Goodbye.")
            break

        action = ACTIONS.get(choice)
        if action is None:
            print("Invalid option. Choose 1-9.")
            continue

        try:
            action(tickets)
        except ValueError as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    main()