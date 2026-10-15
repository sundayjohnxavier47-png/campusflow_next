import copy

from campusflow.notes import add_note
from campusflow.reports import format_report, generate_report
from campusflow.search import (
    format_result_line,
    parse_category_filter,
    parse_priority_filter,
    parse_status_filter,
    search_tickets,
    sort_by_priority,
)
from campusflow.storage import load_tickets, save_tickets
from campusflow.tickets import create_ticket
from campusflow.check_understanding import NOTES_FILE, run_check
from campusflow.workflow import (
    assign_ticket,
    change_status,
    find_ticket,
    get_work_queue,
    reopen_ticket,
)

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
9. Add follow-up note
10. View ticket notes
11. Search tickets
12. Search tickets (sorted by priority)
13. Engineering Understanding Check
0. Exit
"""


def show_ticket(ticket):
    assigned = ticket["assigned_to"] or "unassigned"
    print(
        f'{ticket["id"]} | {ticket["title"]} | {ticket["category"]} | '
        f'urgency: {ticket["urgency"]} | users: {ticket["affected_users"]} | '
        f'priority: {ticket["priority"]} | status: {ticket["status"]} | {assigned}'
    )


def ask(prompt, validator):
    """Keep asking until the validator accepts the input (used for filters)."""
    while True:
        try:
            return validator(input(prompt))
        except ValueError as error:
            print(f"  Error: {error}")


def note_number(note):
    """The number inside a note ID: 'N010' -> 10, so notes sort N002 before N010."""
    digits = "".join(char for char in str(note.get("note_id", "")) if char.isdigit())
    return int(digits) if digits else 0


# ---------------------------------------------------------------------------
# Original handlers (unchanged)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Engineer B: report, notes, search and the understanding check
# ---------------------------------------------------------------------------


def handle_report(tickets):
    print(format_report(generate_report(tickets)))


def handle_note_add(tickets):
    ticket_id = input("Ticket ID: ")
    author = input("Your name (note author): ")
    message = input("Note message (5 to 300 characters): ")
    note = add_note(tickets, ticket_id, author, message)
    save_tickets(tickets)
    print(f"Added note {note['note_id']} to ticket {ticket_id.strip().upper()}.")


def handle_note_view(tickets):
    ticket = find_ticket(tickets, input("Ticket ID: "))
    notes = sorted(ticket.get("notes", []), key=note_number)
    if not notes:
        print(f"Ticket {ticket['id']} has no notes.")
        return
    for note in notes:
        print(f"{note['note_id']} | {note['author']} | {note['message']}")


def read_search_filters():
    """Ask for the four optional filters; blank means 'do not filter'."""
    title = input("Title contains (blank = any): ")
    category = ask(
        "Category (Network/Hardware/Software/Other; blank = any): ",
        parse_category_filter,
    )
    status = ask(
        "Status (open/in_progress/resolved; blank = any): ", parse_status_filter
    )
    priority = ask(
        "Priority (critical/high/medium/low; blank = any): ", parse_priority_filter
    )
    return title, category, status, priority


def show_results(results):
    if not results:
        print("No matching tickets.")
        return
    for ticket in results:
        print(format_result_line(ticket))
    print(f"{len(results)} ticket(s) found.")


def handle_search(tickets):
    title, category, status, priority = read_search_filters()
    show_results(search_tickets(tickets, title, category, status, priority))


def handle_search_sorted(tickets):
    title, category, status, priority = read_search_filters()
    results = search_tickets(tickets, title, category, status, priority)
    show_results(sort_by_priority(results))


def handle_understanding_check(tickets):
    run_check(notes_file=NOTES_FILE)


ACTIONS = {
    "1": handle_create,
    "2": handle_list,
    "3": handle_view,
    "4": handle_assign,
    "5": handle_status,
    "6": handle_reopen,
    "7": handle_queue,
    "8": handle_report,
    "9": handle_note_add,
    "10": handle_note_view,
    "11": handle_search,
    "12": handle_search_sorted,
    "13": handle_understanding_check,
}


def run_menu(tickets):
    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()

        if choice == "0":
            print("Goodbye.")
            break

        action = ACTIONS.get(choice)
        if action is None:
            print("Invalid option. Choose a number from the menu.")
            continue

        # Safety net: if an action fails part-way (for example the disk is
        # full), put the in-memory tickets back exactly as they were.
        snapshot = copy.deepcopy(tickets)
        try:
            action(tickets)
        except ValueError as error:
            tickets[:] = snapshot
            print(f"Error: {error}")
        except OSError as error:
            tickets[:] = snapshot
            print(f"Could not save tickets: {error}")


def main():
    try:
        tickets = load_tickets()
    except ValueError as error:
        print(f"Error: {error}")
        print("Fix or remove data/tickets.json yourself. Nothing was changed.")
        return

    try:
        run_menu(tickets)
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye.")


if __name__ == "__main__":
    main()