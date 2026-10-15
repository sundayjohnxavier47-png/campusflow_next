import json
import os

DEFAULT_PATH = os.path.join("data", "tickets.json")


def load_tickets(path=DEFAULT_PATH):
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(f"Ticket file is corrupted: {error}")

    if not isinstance(data, list):
        raise ValueError("Ticket file is corrupted: expected a list of tickets.")

    return data


def save_tickets(tickets, path=DEFAULT_PATH):
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)

    temp_path = path + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as file:
        json.dump(tickets, file, indent=2)

    os.replace(temp_path, path)