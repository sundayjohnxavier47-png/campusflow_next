# AI Learning Log — Engineer A

## Interaction #1 — Python Unit Testing

**Problem:** I needed to verify that my ticket creation and priority calculation worked correctly.

**My initial understanding:** I knew that tests could check whether my code produced the expected results, but I was not yet confident about writing automated tests.

**Prompt to AI:** Help me run my Python unittest tests and understand the results.

**Useful AI guidance:** I learned how to run tests using `python3 -m unittest discover -s tests -v`.

**My independent experiment/test:** I ran the command in my terminal.

**Verification result:** All 8 tests passed.

**Decision:** I accepted the guidance because the terminal output confirmed that the tests passed.

**Related files:** `tests/test_tickets.py`, `campusflow/tickets.py`

**What I can now explain without AI:** Python's unittest framework checks whether my code behaves as expected. The terminal reports which tests pass and which fail.



## Interaction #2 — Testing Ticket ID Generation and Input Validation

**Problem:** I wanted to verify that ticket IDs remain unique and that invalid user counts are rejected.

**My initial understanding:** I expected the next ticket ID to follow the largest existing numeric ID, and I knew affected users should be a positive integer.

**Prompt to AI:** Help me design small experiments to verify ticket ID generation and input validation without changing my project code.

**Useful AI guidance:** I learned to test edge cases using small Python commands.

**My independent experiment/test:** I tested ticket IDs with existing IDs `T001` and `T003`, then tested ticket creation with `affected_users=2.5`.

**Verification result:** The next ID was `T004`. The decimal input raised the expected `ValueError`.

**Decision:** I accepted the validation behaviour because the actual terminal output confirmed the requirement. The ID experiment also confirmed that the implementation uses the largest existing numeric ID.

**Related file:** `campusflow/tickets.py`

**What I can now explain without AI:** Small experiments help me verify specific behaviours before relying on my code. Invalid input should be rejected instead of being stored as a ticket.



## Interaction #3 — Critically Evaluating Ticket ID Generation

**Problem:** I wanted to check how ticket ID generation behaves when an existing ticket has a malformed ID.

**My initial understanding:** I expected the function to ignore IDs that do not follow the `T` followed by digits format.

**Prompt to AI:** Help me test edge cases in my ticket ID generation and assess whether the results are safe.

**Useful AI guidance:** I learned that testing malformed data can reveal assumptions in an implementation.

**My independent experiment/test:** I created a test list containing `T001` and `TABC`, then created another ticket.

**Verification result:** The function generated `T002`.

**Decision:** The result matched the current implementation. However, I should not automatically assume that ignoring malformed IDs is always safe. If existing data contains duplicate IDs or malformed records, additional validation may be necessary. I will discuss this risk with my partner.

**Related file:** `campusflow/tickets.py`

**What I can now explain without AI:** An experiment confirms what code does in a specific situation, but I must still evaluate whether that behaviour meets the product requirements.