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

---

## Cycle 1 — Validate before you change anything

**Concept gap:** My baseline run showed that the old app only reported a blank title after all four fields had been typed, and I had not thought about the order of checks and changes inside a function.

**Exact question I asked:** "Fix edge cases such as handling errors immediately when they occur, like an empty input, not after everything is done."

**Summary of AI guidance:** Put each rule in one small validator that returns the cleaned value or raises ValueError. In business functions, run every check first and change data last, so a rejected action cannot leave a half-finished change.

**Tiny unrelated experiment (book library):** One function changes the book and then checks the member name; the other checks first and changes last. I called both with a blank member name.

My output:

    bad -> error: Member name cannot be blank.
    bad -> library after failed call: {'Dune': {'borrowed_by': '   '}}
    good -> error: Member name cannot be blank.
    good -> library after failed call: {'Dune': {'borrowed_by': None}}

**Independent verification:** The "bad" version raised the error but still left the library changed. The "good" version left it untouched. In my project, tests/test_safety.py and test_rejected_notes_change_nothing_and_do_not_use_an_id in tests/test_notes.py compare a deep copy of the tickets before and after each rejected action, and they pass.

**Engineering decision:** I adopted central validators in campusflow/validation.py. create_ticket, assign_ticket, change_status and add_note validate everything before changing anything. The immediate-prompt behaviour belongs in main.py, which Engineer B owns, so I will share the validators with them.

**Reflection**
- What I believed before: that validation could happen at the end of the process, as the old app did with the blank title.
- Which claim I tested: that a function which checks after changing leaves bad data behind.
- What the test showed: the failed "bad" call changed the library, and the "good" call did not.
- What I changed in my code: all checks now run before any change in add_note and the workflow functions.
- Test that guards it: tests/test_safety.py.
- Could I explain this without AI: Yes. A function checks everything first and changes data last, so a rejected call leaves the data exactly as it was, and tests/test_safety.py proves it by comparing a copy of the tickets before and after.

## Cycle 2 — JSON can load successfully and still hold unsafe data

**Concept gap:** My earlier ID experiment (T001 and TABC) showed malformed IDs are silently ignored, and I had not considered what else a successfully loaded file could contain.

**Exact question I asked:** "Help me test edge cases in my ticket ID generation and assess whether the results are safe."

**Summary of AI guidance:** json.load only proves the text is valid JSON, not that the business data makes sense. Validate the whole collection after decoding and before using it, and return a new checked list so current memory is never half-overwritten.

**Tiny unrelated experiment:** I decoded a two-item JSON list with the same id twice.

My output:

    [{'id': 'T001'}, {'id': 'T001'}]

**Independent verification:** json.loads accepted the duplicate without complaint, so the duplicate check has to be written by me. In my project, test_duplicate_ids_rejected_and_memory_kept, test_invalid_records_rejected, test_notes_and_next_note_id_survive_reload and test_ids_stay_unique_after_reload in tests/test_storage.py pass.

**Engineering decision:** load_tickets now validates the whole file (structure, required keys, duplicate IDs, standard category and urgency, priority consistency, status rules, note shapes) and returns a new list or raises ValueError. save_tickets refuses to write data that load would reject. Old files without notes still load with an empty notes list.

**Reflection**
- What I believed before: that malformed IDs would simply be ignored, and I had not considered what else a successfully loaded file could contain.
- Which claim I tested: that json.load succeeding means the data is safe.
- What the test showed: duplicates load without any error, so the check has to be mine.
- What I changed in my code: added validate_ticket_collection in campusflow/storage.py.
- Test that guards it: test_duplicate_ids_rejected_and_memory_kept.
- Could I explain this without AI: Yes. json.load only checks the text is valid JSON, so I check the whole list myself (duplicate IDs, bad statuses, wrong priority, malformed notes) and return a new list or raise an error. Because the caller only swaps in the new list when it returns, a bad file can never half-overwrite my tickets.






## Fellow: [Otete Benjamin Agogo] - Engineer B (CampusFlow Next)

### CampusFlow Next - Cycle 1: Replacing regex with plain string methods (AI suggestion CHANGED)

- **Concept gap (what I did not understand before):** I did not understand regular expressions (regex). The first ID helper I was given used `re.compile(rf"^{re.escape(prefix)}(\d+)$", re.IGNORECASE)`. I could not explain what the pattern did, so I could not defend it in front of a mentor.

- **Exact question I asked the AI:** "please, I do not understand regex, and I do not want to use, I can not defend it. replace this file."

- **Summary of the AI's guidance:** The AI replaced the regex with four plain steps: (1) make the text upper case and check it `startswith` the prefix; (2) cut the prefix off with slicing, `id_text[len(prefix):]`; (3) check that what is left is only digits with `isascii()` and `isdigit()`; (4) turn it into a number with `int()` and keep the largest one. It also pointed out that two other files at that time still used regex and offered versions without it.

- **My tiny unrelated experiment (book shelf IDs, nothing from CampusFlow):**

  ```python
  import re

  def with_regex(text, prefix):
      match = re.match(rf"^{re.escape(prefix)}(\d+)$", text, re.IGNORECASE)
      return int(match.group(1)) if match else None

  def with_string_methods(text, prefix):
      text = str(text).strip().upper()
      if not text.startswith(prefix.upper()):
          return None
      digits = text[len(prefix):]
      if digits.isascii() and digits.isdigit():
          return int(digits)
      return None

  for text in ["B007", "b012", "B", "BX1", "B1_0", "C005"]:
      print(repr(text), with_regex(text, "B"), with_string_methods(text, "B"))

  print(int("1_0"))
  ```

  Result: both versions gave the same answer on all six inputs (`7`, `12`, `None`, `None`, `None`, `None`), and `int("1_0")` printed `10`.

- **Independent verification:** The comparison above shows the regex version was not wrong. The last line shows why the `isdigit()` check matters: `int()` on its own accepts text like `"1_0"` as the number 10, so the digits must be checked before converting. I also ran the whole project suite with `python3 -m unittest discover -s tests -v` and the ID-related tests still passed.

- **Did I accept, change or reject the AI's suggestion?** Changed. I did not reject the regex because it gave wrong answers (the experiment shows it did not). I rejected it because I could not explain it, and a rule I cannot explain I cannot defend or maintain.

- **Final engineering decision in my code:** I use only plain string methods. None of my files (`search.py`, `reports.py`, `questions.py`, `understanding_check.py`, `main.py`) contains regex. Check: `grep -rn "import re" campusflow main.py` shows nothing from my files.

- **Reflection**
  - What did I believe before? That a solution that works is enough. I had not asked whether I could explain it.
  - What did the AI explain? How to do the same job with `startswith`, slicing, `isdigit` and `int`.
  - Which claim did I test? That the plain version behaves exactly like the regex version.
  - What did the test show? Identical results on all six inputs, and that `int("1_0")` is 10, so the digit check is needed.
  - Which test guards this learning against future regression? The ID tests in the unit-test suite (new IDs continue from the highest number; malformed IDs are ignored).
  - Could I explain this choice without AI in the room? Yes: "Cut off the prefix, check the rest is digits, convert to a number, keep the biggest, add one."

---
