import copy
import unittest

from campusflow.notes import add_note, get_notes, next_note_id
from campusflow.tickets import create_ticket
from campusflow.workflow import assign_ticket, change_status, reopen_ticket


class TestNotes(unittest.TestCase):

    def setUp(self):
        self.tickets = []
        create_ticket(self.tickets, "Wi-Fi down", "Network", "high", 12)

    def resolve_ticket(self):
        assign_ticket(self.tickets, "T001", "Ada")
        change_status(self.tickets, "T001", "in_progress")
        change_status(self.tickets, "T001", "resolved")

    def test_new_ticket_starts_with_empty_notes(self):
        self.assertEqual(self.tickets[0]["notes"], [])

    def test_valid_notes_get_sequential_ids(self):
        first = add_note(self.tickets, "T001", "Mentor A", "Wi-Fi router reboot attempted")
        second = add_note(self.tickets, "T001", "Mentor B", "Investigating switch ports")
        self.assertEqual(first["note_id"], "N001")
        self.assertEqual(second["note_id"], "N002")
        self.assertEqual(len(self.tickets[0]["notes"]), 2)

    def test_note_text_is_trimmed(self):
        note = add_note(self.tickets, "T001", "  Mentor A ", "  Router rebooted  ")
        self.assertEqual(note["author"], "Mentor A")
        self.assertEqual(note["message"], "Router rebooted")

    def test_rejected_notes_change_nothing_and_do_not_use_an_id(self):
        add_note(self.tickets, "T001", "Mentor A", "First valid note")
        before = copy.deepcopy(self.tickets)

        bad_inputs = [
            ("Mentor A", "    "),                    # blank message
            ("Mentor A", "abcd"),                    # 4 characters, too short
            ("Mentor A", "x" * 301),                 # too long
            ("   ", "A perfectly fine message"),     # blank author
            (None, "A perfectly fine message"),      # author is not text
            ("Mentor A", None),                      # message is not text
        ]
        for author, message in bad_inputs:
            with self.assertRaises(ValueError):
                add_note(self.tickets, "T001", author, message)
            self.assertEqual(self.tickets, before)

        next_valid = add_note(self.tickets, "T001", "Mentor A", "Second valid note")
        self.assertEqual(next_valid["note_id"], "N002")

    def test_message_length_boundaries(self):
        self.assertEqual(add_note(self.tickets, "T001", "A", "12345")["note_id"], "N001")
        self.assertEqual(add_note(self.tickets, "T001", "A", "x" * 300)["note_id"], "N002")

    def test_resolved_ticket_rejects_note_until_reopened(self):
        add_note(self.tickets, "T001", "Mentor A", "Wi-Fi router reboot attempted")
        add_note(self.tickets, "T001", "Mentor B", "Investigating switch ports")
        self.resolve_ticket()

        before = copy.deepcopy(self.tickets)
        with self.assertRaises(ValueError):
            add_note(self.tickets, "T001", "Mentor A", "Trying to add a late note")
        self.assertEqual(self.tickets, before)

        reopen_ticket(self.tickets, "T001")
        note = add_note(self.tickets, "T001", "Mentor A", "Back to investigate")
        self.assertEqual(note["note_id"], "N003")
        self.assertEqual(len(get_notes(self.tickets, "T001")), 3)

    def test_in_progress_ticket_accepts_notes(self):
        assign_ticket(self.tickets, "T001", "Ada")
        change_status(self.tickets, "T001", "in_progress")
        note = add_note(self.tickets, "T001", "Ada", "Started on the fix")
        self.assertEqual(note["note_id"], "N001")

    def test_unknown_ticket_rejected(self):
        with self.assertRaises(ValueError):
            add_note(self.tickets, "T999", "Ada", "This ticket does not exist")

    def test_note_ids_are_per_ticket(self):
        create_ticket(self.tickets, "Laptop", "Hardware", "low", 1)
        add_note(self.tickets, "T001", "Ada", "Note on the first ticket")
        note = add_note(self.tickets, "T002", "Ada", "Note on the second ticket")
        self.assertEqual(note["note_id"], "N001")

    def test_next_note_id_ignores_malformed_ids_and_old_tickets(self):
        old_style_ticket = {"id": "T009"}  # saved before notes existed
        self.assertEqual(next_note_id(old_style_ticket), "N001")

        ticket = {"notes": [{"note_id": "N002"}, {"note_id": "oops"}, "junk"]}
        self.assertEqual(next_note_id(ticket), "N003")


if __name__ == "__main__":
    unittest.main()