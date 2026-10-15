# Baseline Check — Engineer A

## What I ran

- Commit: original audited CampusFlow code (main, commit 594f8a9)
- Run the app: `python3 main.py`
- Run the tests: `python3 -m unittest discover -s tests -v`

## Test result

24 tests ran. All 24 passed (OK).

## Three inputs I tested

1. Blank title with valid other fields (title empty, Network, high, 15).
   Result: the app asked for all four fields first, then printed "Error: Title cannot be blank." and returned to the menu. Everything typed was lost.
   Status: reproduced (confirmed).

2. Several bad fields at once (title "ner", category "soft", urgency "baa", affected users "abg").
   Result: only one error was shown, "Category must be Network, Hardware, Software, or Other." The bad urgency and the non-numeric affected users were never reported, so the user would have to fix them one retry at a time.
   Status: reproduced (confirmed).

3. A normal flow: create a ticket (bad network, Network, high, 70), assign it to Kingsley using lowercase "t001", then move it to in_progress.
   Result: the ticket was created as critical, the lowercase ID was accepted, and the status changed to in_progress correctly.
   Status: works as expected.

## What my audit said needed improvement

(Write here, in your own words, the points from your audit feedback.)

## Other risks noticed in code review (not yet reproduced)

- Ctrl+C at a prompt may show a traceback.
- If saving fails after a ticket is added in memory, memory and file could disagree.
- Loading a file only checks that it is a list, so duplicate IDs or missing fields could load and crash later.
- Reports have no category counts, unresolved count, or resolution percentage.

These are not labelled as confirmed bugs until I reproduce them.