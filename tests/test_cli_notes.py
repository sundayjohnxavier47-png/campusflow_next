import json
import json
import unittest

import main as menu

def test_rejected_note_does_not_save(tmp_path, monkeypatch, capsys):
    tickets = [{
        "id": "T001", "title": "Wifi down", "category": "Network",
        "urgency": "high", "affected_users": 50, "priority": "critical",
        "status": "resolved", "assigned_to": "Ana", "notes": [],
    }]

    ticket_file = tmp_path / "tickets.json"
    ticket_file.write_text(json.dumps(tickets, indent=2))
    before = ticket_file.read_bytes()

    save_calls = []
    monkeypatch.setattr(menu, "save_tickets", lambda data: save_calls.append(1))

    # option 9, ticket ID, then exit. No author or message is requested.
    answers = iter(["9", "T001", "0"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))

    menu.run_menu(tickets)

    out = capsys.readouterr().out
    assert "Cannot complete action:" in out   # matches the new run_menu prefix
    assert "Reopen the ticket first" in out
    assert save_calls == []
    assert ticket_file.read_bytes() == before
    assert tickets[0]["notes"] == []



    if __name__ == "__main__":
        unittest.main()