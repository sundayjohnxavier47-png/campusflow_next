import unittest

from campusflow.tickets import create_ticket
from campusflow.workflow import (
    assign_ticket,
    change_status,
    find_ticket,
    get_work_queue,
    reopen_ticket,
)
from campusflow.reports import generate_report


class TestWorkflow(unittest.TestCase):

    def setUp(self):
        self.tickets = []
        create_ticket(self.tickets, "Wi-Fi down", "Network", "high", 12)

    def test_unassigned_ticket_cannot_start(self):
        with self.assertRaises(ValueError):
            change_status(self.tickets, "T001", "in_progress")
        self.assertEqual(self.tickets[0]["status"], "open")

    def test_full_lifecycle(self):
        assign_ticket(self.tickets, "T001", "Ada")
        change_status(self.tickets, "T001", "in_progress")
        change_status(self.tickets, "T001", "resolved")
        self.assertEqual(self.tickets[0]["status"], "resolved")

    def test_invalid_transition_rejected(self):
        assign_ticket(self.tickets, "T001", "Ada")
        with self.assertRaises(ValueError):
            change_status(self.tickets, "T001", "resolved")
        self.assertEqual(self.tickets[0]["status"], "open")

    def test_unknown_ticket_id_rejected(self):
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T999", "Ada")

    def test_blank_staff_name_rejected(self):
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", "   ")
        self.assertIsNone(self.tickets[0]["assigned_to"])

    def test_resolved_ticket_cannot_be_assigned_until_reopened(self):
        assign_ticket(self.tickets, "T001", "Ada")
        change_status(self.tickets, "T001", "in_progress")
        change_status(self.tickets, "T001", "resolved")
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", "Bola")
        reopen_ticket(self.tickets, "T001")
        self.assertEqual(find_ticket(self.tickets, "T001")["status"], "open")

    def test_cannot_reopen_ticket_that_is_not_resolved(self):
        with self.assertRaises(ValueError):
            reopen_ticket(self.tickets, "T001")


class TestQueueAndReports(unittest.TestCase):

    def test_queue_sorted_by_priority_then_id(self):
        tickets = []
        create_ticket(tickets, "Printer", "Hardware", "low", 1)      # T001 low
        create_ticket(tickets, "Wi-Fi", "Network", "high", 12)       # T002 critical
        create_ticket(tickets, "Laptop", "Hardware", "high", 2)      # T003 high
        create_ticket(tickets, "Portal", "Software", "high", 2)      # T004 high

        order = [t["id"] for t in get_work_queue(tickets)]
        self.assertEqual(order, ["T002", "T003", "T004", "T001"])

    def test_queue_only_contains_open_tickets(self):
        tickets = []
        create_ticket(tickets, "Wi-Fi", "Network", "high", 12)
        assign_ticket(tickets, "T001", "Ada")
        change_status(tickets, "T001", "in_progress")
        self.assertEqual(get_work_queue(tickets), [])

    def test_empty_report(self):
        report = generate_report([])
        self.assertEqual(report["total"], 0)
        self.assertEqual(report["by_status"]["open"], 0)
        self.assertEqual(report["by_priority"]["critical"], 0)

    def test_report_counts(self):
        tickets = []
        create_ticket(tickets, "Wi-Fi", "Network", "high", 12)
        create_ticket(tickets, "Printer", "Hardware", "low", 1)
        report = generate_report(tickets)
        self.assertEqual(report["total"], 2)
        self.assertEqual(report["by_priority"]["critical"], 1)
        self.assertEqual(report["by_priority"]["low"], 1)
        self.assertEqual(report["by_status"]["open"], 2)


if __name__ == "__main__":
    unittest.main()