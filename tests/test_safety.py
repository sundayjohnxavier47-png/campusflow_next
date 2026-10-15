import copy
import unittest

from campusflow.notes import add_note
from campusflow.tickets import create_ticket
from campusflow.workflow import assign_ticket, change_status, reopen_ticket


class TestFailedActionsChangeNothing(unittest.TestCase):
    """Every rejected action must leave the WHOLE ticket collection unchanged."""

    def setUp(self):
        self.tickets = []
        create_ticket(self.tickets, "Wi-Fi down", "Network", "high", 12)   # T001 open
        create_ticket(self.tickets, "Laptop", "Hardware", "low", 1)        # T002
        assign_ticket(self.tickets, "T002", "Ada")
        change_status(self.tickets, "T002", "in_progress")
        change_status(self.tickets, "T002", "resolved")                    # T002 resolved
        self.before = copy.deepcopy(self.tickets)

    def assert_unchanged(self):
        self.assertEqual(self.tickets, self.before)

    def test_invalid_create_inputs_change_nothing(self):
        bad_inputs = [
            ("   ", "Network", "high", 5),
            ("Title", "Plumbing", "high", 5),
            ("Title", "Network", "urgent", 5),
            ("Title", "Network", "high", 0),
            ("Title", "Network", "high", -3),
            ("Title", "Network", "high", 2.5),
            ("Title", "Network", "high", "5"),
            ("Title", "Network", "high", True),
        ]
        for args in bad_inputs:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    create_ticket(self.tickets, *args)
                self.assert_unchanged()

    def test_invalid_assignments_change_nothing(self):
        bad_calls = [
            ("T001", "   "),     # blank staff name
            ("T001", None),      # staff name not text
            ("T999", "Ada"),     # unknown ticket
            ("hello", "Ada"),    # not a ticket ID
            ("T002", "Bola"),    # resolved ticket
        ]
        for ticket_id, staff in bad_calls:
            with self.subTest(ticket_id=ticket_id, staff=staff):
                with self.assertRaises(ValueError):
                    assign_ticket(self.tickets, ticket_id, staff)
                self.assert_unchanged()

    def test_invalid_status_changes_change_nothing(self):
        bad_calls = [
            ("T001", "in_progress"),  # unassigned ticket
            ("T001", "resolved"),     # skips in_progress
            ("T001", "done"),         # not a real status
            ("T001", None),           # status not text
            ("T999", "in_progress"),  # unknown ticket
            ("T002", "open"),         # resolved ticket must be reopened
            ("T002", "in_progress"),  # resolved ticket
        ]
        for ticket_id, status in bad_calls:
            with self.subTest(ticket_id=ticket_id, status=status):
                with self.assertRaises(ValueError):
                    change_status(self.tickets, ticket_id, status)
                self.assert_unchanged()

    def test_skipping_a_step_on_an_assigned_ticket_changes_nothing(self):
        assign_ticket(self.tickets, "T001", "Ada")
        before = copy.deepcopy(self.tickets)

        with self.assertRaises(ValueError):
            change_status(self.tickets, "T001", "resolved")

        self.assertEqual(self.tickets, before)

    def test_reopening_a_ticket_that_is_not_resolved_changes_nothing(self):
        with self.assertRaises(ValueError):
            reopen_ticket(self.tickets, "T001")
        self.assert_unchanged()

    def test_invalid_notes_change_nothing(self):
        bad_calls = [
            ("T002", "Mentor A", "Note on a resolved ticket"),  # resolved
            ("T001", "Mentor A", "abc"),                        # too short
            ("T001", "Mentor A", "x" * 301),                    # too long
            ("T001", "   ", "A perfectly fine message"),        # blank author
            ("T999", "Mentor A", "Ticket does not exist"),      # unknown ticket
        ]
        for ticket_id, author, message in bad_calls:
            with self.subTest(ticket_id=ticket_id, author=author):
                with self.assertRaises(ValueError):
                    add_note(self.tickets, ticket_id, author, message)
                self.assert_unchanged()


if __name__ == "__main__":
    unittest.main()