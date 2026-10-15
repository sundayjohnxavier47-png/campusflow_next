import copy
import json
import os
import tempfile
import unittest

from campusflow.notes import add_note
from campusflow.storage import load_tickets, save_tickets
from campusflow.tickets import create_ticket


class TestStorage(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.folder.name, "tickets.json")

    def tearDown(self):
        self.folder.cleanup()

    # ---- helpers ----
    def write_raw(self, data):
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(data, file)

    def good_ticket(self, **changes):
        ticket = {
            "id": "T001", "title": "Wi-Fi down", "category": "Network",
            "urgency": "high", "affected_users": 12, "priority": "critical",
            "status": "open", "assigned_to": None, "notes": [],
        }
        ticket.update(changes)
        return ticket

    # ---- original tests ----
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

    # ---- new tests ----
    def test_notes_and_next_note_id_survive_reload(self):
        tickets = []
        create_ticket(tickets, "Wi-Fi down", "Network", "high", 12)
        add_note(tickets, "T001", "Mentor A", "Router reboot attempted")
        add_note(tickets, "T001", "Mentor B", "Investigating switch ports")
        save_tickets(tickets, self.path)

        reloaded = load_tickets(self.path)
        self.assertEqual(reloaded, tickets)

        note = add_note(reloaded, "T001", "Mentor A", "Back to investigate")
        self.assertEqual(note["note_id"], "N003")

    def test_old_file_without_notes_still_loads(self):
        old_ticket = self.good_ticket()
        del old_ticket["notes"]
        self.write_raw([old_ticket])

        loaded = load_tickets(self.path)
        self.assertEqual(loaded[0]["id"], "T001")
        self.assertEqual(loaded[0]["notes"], [])

    def test_duplicate_ids_rejected_and_memory_kept(self):
        memory = [self.good_ticket(id="T005")]
        before = copy.deepcopy(memory)
        self.write_raw([self.good_ticket(), self.good_ticket()])

        with self.assertRaises(ValueError):
            memory = load_tickets(self.path)  # raises, so memory is not replaced

        self.assertEqual(memory, before)

    def test_invalid_records_rejected(self):
        missing_status = self.good_ticket()
        del missing_status["status"]

        bad_files = {
            "missing key": [missing_status],
            "not a record": ["junk"],
            "bad status": [self.good_ticket(status="done")],
            "priority mismatch": [self.good_ticket(priority="low")],
            "category not standard": [self.good_ticket(category="network")],
            "bad urgency": [self.good_ticket(urgency="urgent")],
            "boolean users": [self.good_ticket(affected_users=True)],
            "zero users": [self.good_ticket(affected_users=0)],
            "blank title": [self.good_ticket(title="  ")],
            "bad ticket id": [self.good_ticket(id="TABC")],
            "in_progress but unassigned": [self.good_ticket(status="in_progress")],
            "notes not a list": [self.good_ticket(notes="oops")],
            "note missing key": [self.good_ticket(notes=[
                {"note_id": "N001", "author": "A"},
            ])],
            "duplicate note ids": [self.good_ticket(notes=[
                {"note_id": "N001", "author": "A", "message": "First note"},
                {"note_id": "N001", "author": "B", "message": "Second note"},
            ])],
            "note too short": [self.good_ticket(notes=[
                {"note_id": "N001", "author": "A", "message": "abc"},
            ])],
            "bad note id": [self.good_ticket(notes=[
                {"note_id": "X001", "author": "A", "message": "A fine message"},
            ])],
        }

        for name, data in bad_files.items():
            with self.subTest(name):
                self.write_raw(data)
                with self.assertRaises(ValueError):
                    load_tickets(self.path)

    def test_save_refuses_invalid_data_and_keeps_old_file(self):
        good = []
        create_ticket(good, "Wi-Fi down", "Network", "high", 12)
        save_tickets(good, self.path)
        with open(self.path, "r", encoding="utf-8") as file:
            original = file.read()

        bad = copy.deepcopy(good)
        bad.append(copy.deepcopy(good[0]))  # same ID twice

        with self.assertRaises(ValueError):
            save_tickets(bad, self.path)

        with open(self.path, "r", encoding="utf-8") as file:
            self.assertEqual(file.read(), original)
        self.assertFalse(os.path.exists(self.path + ".tmp"))


if __name__ == "__main__":
    unittest.main()