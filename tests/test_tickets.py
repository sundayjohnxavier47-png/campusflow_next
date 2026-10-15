
import unittest

from campusflow.tickets import calculate_priority, create_ticket


class TestTicketPriority(unittest.TestCase):

    def test_critical_priority(self):
        self.assertEqual(calculate_priority("high", 12), "critical")

    def test_high_priority(self):
        self.assertEqual(calculate_priority("high", 2), "high")

    def test_medium_priority(self):
        self.assertEqual(calculate_priority("low", 4), "medium")

    def test_low_priority(self):
        self.assertEqual(calculate_priority("low", 1), "low")


class TestTicketCreation(unittest.TestCase):

    def test_create_ticket(self):
        tickets = []

        ticket = create_ticket(
            tickets, "Wi-Fi is down", "Network", "high", 12
        )

        self.assertEqual(ticket["id"], "T001")
        self.assertEqual(ticket["priority"], "critical")
        self.assertEqual(ticket["status"], "open")
        self.assertIsNone(ticket["assigned_to"])

    def test_ticket_ids_are_unique(self):
        tickets = []

        first = create_ticket(tickets, "Wi-Fi issue", "Network", "high", 12)
        second = create_ticket(tickets, "Laptop issue", "Hardware", "low", 1)

        self.assertEqual(first["id"], "T001")
        self.assertEqual(second["id"], "T002")

    def test_reject_zero_affected_users(self):
        with self.assertRaises(ValueError):
            create_ticket([], "Wi-Fi issue", "Network", "high", 0)

    def test_reject_blank_title(self):
        with self.assertRaises(ValueError):
            create_ticket([], "   ", "Network", "high", 5)


if __name__ == "__main__":
    unittest.main()

