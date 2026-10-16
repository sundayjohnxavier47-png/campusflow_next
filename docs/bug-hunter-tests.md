# Bug-Hunter Tests

Each engineer devises ONE edge case that is not on the sprint guide's list, aimed at the OTHER engineer's module. The best test makes an important invariant visible.

---

## Bug-hunter test 1 — written by Engineer A, aimed at Engineer B's module (search, reports, CLI, quiz)

*(Engineer A completes this section.)*

- **Test name:** `[test_...]`
- **File:** `[tests/test_....py]`
- **Invariant it protects:** `[one sentence]`
- **Initial state:** `[the tickets or file contents before the action]`
- **Input:** `[exact call or typed values]`
- **Expected result:** `[what should happen]`
- **Actual result:** `[what happened when you ran it]`
- **Code change made (or "none needed"):** `[describe]`

---

## Bug-hunter test 2 — written by Engineer B ([Otete Benjamin Agogo]), aimed at Engineer A's module (validation, notes, storage)

- **Test name:** `test_original_sample_ticket_still_loads` (with four companion tests in the same class, `TestOriginalTicketFileStillOpens`)

- **File:** `tests/test_legacy_data.py`

- **Invariant it protects:** Tickets saved by the original version of CampusFlow must still open. The sprint guide says old working tickets must not be discarded. A strict loader is good, but it must not turn a valid old ticket file into "corrupted".

- **Initial state:** A data file written by the original version, containing one ticket and no `notes` field:

  ```json
  [{"id": "T001", "title": "Blocked Drainage", "category": "other",
    "urgency": "high", "affected_users": 16, "priority": "critical",
    "status": "open", "assigned_to": "none"}]
  ```

  Two things about this ticket are different from the new standard: the category is written `"other"` in lower case, and the assignee is the text `"none"` instead of `null`.

- **Input:** `load_tickets(path_to_that_file)`, or starting the application with this file as `data/tickets.json`.

- **Expected result:** The load succeeds and returns one ticket. The category becomes `"Other"`, `assigned_to` becomes `None` (unassigned), `notes` becomes `[]`, the priority stays `critical`, and the file on disk is not rewritten by loading. The ticket still cannot move to `in_progress` until it is assigned.

- **Actual result:** The load is refused. The loader checks that the category is already in its standard form, `"other"` is not, so it raises `ValueError: Ticket file is corrupted: ticket #1 (T001): category is not in its standard form.` and the application stops at start-up with "Nothing was changed."
  *(To confirm before you submit: run `python3 -m unittest tests.test_legacy_data -v` before A adds the fix and copy the failure message you see.)*

- **Why the second difference matters:** The text `"none"` is a non-empty string, so the workflow would treat that ticket as already assigned and allow an open ticket to start work without an owner. That breaks the rule "an unassigned ticket cannot enter in_progress".

- **Code change made:** Raised as a review comment on A's pull request with a suggested `upgrade_legacy_ticket` function in `storage.py`. It adds `notes: []`, fixes the case of category and urgency, and turns placeholder assignees such as `"none"` into `null`. Only old records (those with no `notes` field) are upgraded, so new-format files are still checked strictly. After the fix, the five tests in `tests/test_legacy_data.py` pass.
  *(Replace "Raised as a review comment" with the pull request link once you have posted it.)*