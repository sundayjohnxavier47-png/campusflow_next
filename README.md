# CampusFlow Next

A command-line helpdesk ticket manager for campus support staff. It records technical problems (Wi-Fi outages, faulty laptops, broken software), calculates how urgent each one is, assigns it to a staff member, tracks its progress, keeps follow-up notes, and saves everything to a JSON file. Python standard library only, no packages to install.

## Setup

    git clone https://github.com/sundayjohnxavier47-png/campusflow_next.git
    cd campusflow_next

Requires Python 3.

## Run the app

    python3 main.py

Menu options:

1. Create ticket
2. List all tickets
3. View one ticket
4. Assign ticket
5. Change status
6. Reopen ticket
7. Work queue
8. Report
9. Exit

## Run the tests

    python3 -m unittest discover -s tests -v

## Ticket rules

- Category: Network, Hardware, Software or Other. Urgency: low, medium or high.
- The title cannot be blank. Affected users must be a positive whole number (no decimals, text or booleans).
- Priority is checked in this order and the first match wins: high urgency and 10 or more affected users is critical; high urgency or 10 or more affected users is high; medium urgency or 3 or more affected users is medium; anything else is low.
- Status flow: open, then in_progress, then resolved. A ticket must be assigned before it can move to in_progress. A resolved ticket cannot be changed until it is reopened, which sets it back to open.
- The work queue lists only open tickets, from critical to low. Tickets with the same priority are ordered by ticket number.
- Invalid actions raise ValueError and change nothing.

## Known limitations

- Text interface only. Staff names are free text.
- Tickets cannot be edited or deleted after creation.

## CampusFlow Next

### Team

- Engineer A: sundayjohnxavier47-png (validation, status protection, follow-up notes, JSON storage)
- Engineer B: benjaminagogo1 (search, reports, CLI menus, understanding check)

### Follow-up notes

- Added with add_note(tickets, ticket_id, author, message) in campusflow/notes.py; read with get_notes.
- Only open or in_progress tickets accept notes. The author cannot be blank. The message must be 5 to 300 characters after trimming.
- Note IDs are per ticket (N001, N002...). A rejected note does not use an ID. Notes are kept through resolve and reopen.
- Invalid actions raise ValueError and change nothing.

### Data file format

Tickets are saved to data/tickets.json as a JSON list of ticket records:

    [
      {
        "id": "T001",
        "title": "Wi-Fi down",
        "category": "Network",
        "urgency": "high",
        "affected_users": 12,
        "priority": "critical",
        "status": "open",
        "assigned_to": null,
        "notes": [
          {"note_id": "N001", "author": "Mentor A", "message": "Router reboot attempted"}
        ]
      }
    ]

Loading checks the whole file first. It is rejected, and current data stays unchanged, if the JSON is corrupt, a ticket is missing a field, ticket IDs repeat, category, urgency, status or priority are inconsistent, an in_progress or resolved ticket is unassigned, or a note is malformed. Older files without a notes field still load (notes become an empty list). Saving refuses data that loading would reject. Next ticket and note IDs are worked out from the existing records, so they never collide after a reload.