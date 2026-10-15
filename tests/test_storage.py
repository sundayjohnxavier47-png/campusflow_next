import json
import os
import tempfile
import unittest

from campusflow.tickets import create_ticket
from campusflow.storage import load_tickets, save_tickets


class TestStorage(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.folder.name, "tickets.json")

    def tearDown(self):
        self.folder.cleanup()

    def test_missing_file_starts_fresh(self):
        self.assertEqual(load_tickets(self.path), [])

    def test_save_and_reload_preserves_tickets(self):
        tickets = []
        create_ticket(tickets, "Wi-Fi down", "Network", "high", 12)
        save_tickets(tickets, self.path)

        self.assertEqual(load_tickets(self.path), tickets)

    def test_ids_stay_unique_after_reload(self):
        tickets = []
        create_ticket(tickets, "Wi-Fi down", "Network", "high", 12)
        save_tickets(tickets, self.path)

        reloaded = load_tickets(self.path)
        new_ticket = create_ticket(reloaded, "Laptop", "Hardware", "low", 1)

        self.assertEqual(new_ticket["id"], "T002")

    def test_corrupted_json_raises_and_keeps_file(self):
        with open(self.path, "w", encoding="utf-8") as file:
            file.write("{ this is not valid json")

        with self.assertRaises(ValueError):
            load_tickets(self.path)

        with open(self.path, "r", encoding="utf-8") as file:
            self.assertEqual(file.read(), "{ this is not valid json")

    def test_wrong_json_shape_rejected(self):
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump({"not": "a list"}, file)

        with self.assertRaises(ValueError):
            load_tickets(self.path)


if __name__ == "__main__":
    unittest.main()