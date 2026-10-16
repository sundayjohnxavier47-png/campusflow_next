import copy
import unittest

from campusflow.search import (
    format_result_line,
    parse_category_filter,
    parse_priority_filter,
    parse_status_filter,
    search_tickets,
    sort_by_priority,
)


def make_ticket(ticket_id, title, category, priority, status, assigned_to=None):
    return {
        "id": ticket_id,
        "title": title,
        "category": category,
        "urgency": "medium",
        "affected_users": 1,
        "priority": priority,
        "status": status,
        "assigned_to": assigned_to,
        "notes": [],
    }


def sample_tickets():
    return [
        make_ticket("T001", "Wifi down in library", "Network", "high", "open"),
        make_ticket("T002", "WiFi slow in hostel", "Network", "medium", "in_progress", "Ana"),
        make_ticket("T003", "Wi-Fi login fails", "Network", "low", "resolved", "Ben"),
        make_ticket("T004", "Laptop screen broken", "Hardware", "critical", "open"),
        make_ticket("T005", "Install wifi driver", "Software", "high", "open"),
    ]


def ids(tickets):
    return [ticket["id"] for ticket in tickets]


class TestTitleSearch(unittest.TestCase):
    def setUp(self):
        self.tickets = sample_tickets()

    def test_title_ignores_case(self):
        self.assertEqual(ids(search_tickets(self.tickets, "WIFI")), ["T001", "T002", "T005"])
        self.assertEqual(ids(search_tickets(self.tickets, "wifi")), ["T001", "T002", "T005"])

    def test_title_matches_a_substring(self):
        self.assertEqual(ids(search_tickets(self.tickets, "down")), ["T001"])

    def test_punctuation_must_match_exactly(self):
        self.assertEqual(ids(search_tickets(self.tickets, "wi-fi")), ["T003"])
        self.assertEqual(ids(search_tickets(self.tickets, "WI-FI")), ["T003"])
        self.assertNotIn("T003", ids(search_tickets(self.tickets, "wifi")))

    def test_blank_or_none_title_means_no_filter(self):
        everything = ids(self.tickets)
        self.assertEqual(ids(search_tickets(self.tickets, "")), everything)
        self.assertEqual(ids(search_tickets(self.tickets, "   ")), everything)
        self.assertEqual(ids(search_tickets(self.tickets, None)), everything)

    def test_no_match_returns_empty_list(self):
        self.assertEqual(search_tickets(self.tickets, "printer"), [])

    def test_empty_ticket_list_returns_empty_list(self):
        self.assertEqual(search_tickets([], "wifi", "Network", "open", "high"), [])


class TestCombinedFilters(unittest.TestCase):
    def setUp(self):
        self.tickets = sample_tickets()

    def test_all_supplied_filters_must_match(self):
        # wifi + Network + open: T002 is in_progress, T005 is Software.
        result = search_tickets(self.tickets, "wifi", "Network", "open")
        self.assertEqual(ids(result), ["T001"])

    def test_filters_are_and_not_or(self):
        by_category = set(ids(search_tickets(self.tickets, category="Network")))
        by_status = set(ids(search_tickets(self.tickets, status="open")))
        combined = set(ids(search_tickets(self.tickets, category="Network", status="open")))
        self.assertEqual(combined, by_category & by_status)
        self.assertNotEqual(combined, by_category | by_status)

    def test_category_is_case_insensitive(self):
        self.assertEqual(ids(search_tickets(self.tickets, category="network")), ["T001", "T002", "T003"])

    def test_status_and_priority_filters(self):
        self.assertEqual(ids(search_tickets(self.tickets, status="open")), ["T001", "T004", "T005"])
        self.assertEqual(ids(search_tickets(self.tickets, priority="high")), ["T001", "T005"])
        self.assertEqual(ids(search_tickets(self.tickets, status="open", priority="critical")), ["T004"])

    def test_empty_filters_return_everything_in_original_order(self):
        self.assertEqual(ids(search_tickets(self.tickets)), ids(self.tickets))

    def test_invalid_filters_raise_value_error(self):
        with self.assertRaises(ValueError):
            search_tickets(self.tickets, category="Printer")
        with self.assertRaises(ValueError):
            search_tickets(self.tickets, status="closed")
        with self.assertRaises(ValueError):
            search_tickets(self.tickets, priority="urgent")

    def test_search_does_not_modify_tickets(self):
        before = copy.deepcopy(self.tickets)
        search_tickets(self.tickets, "wifi", "Network", "open", "high")
        self.assertEqual(self.tickets, before)


class TestFilterParsers(unittest.TestCase):
    def test_blank_means_no_filter(self):
        self.assertEqual(parse_category_filter(""), "")
        self.assertEqual(parse_category_filter(None), "")
        self.assertEqual(parse_status_filter("  "), "")
        self.assertEqual(parse_priority_filter(""), "")

    def test_valid_values_are_normalised(self):
        self.assertEqual(parse_category_filter(" hardware "), "Hardware")
        self.assertEqual(parse_status_filter("IN_PROGRESS"), "in_progress")
        self.assertEqual(parse_priority_filter(" Critical "), "critical")

    def test_invalid_values_raise_value_error(self):
        for parser, bad in (
            (parse_category_filter, "Printer"),
            (parse_status_filter, "closed"),
            (parse_priority_filter, "urgent"),
        ):
            with self.subTest(parser=parser.__name__):
                with self.assertRaises(ValueError):
                    parser(bad)


class TestSortByPriority(unittest.TestCase):
    def test_sorted_by_priority_then_id(self):
        result = sort_by_priority(sample_tickets())
        self.assertEqual(ids(result), ["T004", "T001", "T005", "T002", "T003"])

    def test_ids_compare_as_numbers_not_text(self):
        tickets = [
            make_ticket("T10", "Ten", "Other", "high", "open"),
            make_ticket("T2", "Two", "Other", "high", "open"),
            make_ticket("T1", "One", "Other", "high", "open"),
        ]
        self.assertEqual(ids(sort_by_priority(tickets)), ["T1", "T2", "T10"])

    def test_sort_returns_new_list_and_keeps_original_order(self):
        tickets = sample_tickets()
        original_order = ids(tickets)
        result = sort_by_priority(tickets)
        self.assertIsNot(result, tickets)
        self.assertEqual(ids(tickets), original_order)

    def test_sort_does_not_filter_by_status(self):
        result = sort_by_priority(sample_tickets())
        self.assertIn("resolved", [ticket["status"] for ticket in result])
        self.assertEqual(len(result), 5)


class TestFormatResultLine(unittest.TestCase):
    def test_line_shows_required_fields(self):
        ticket = make_ticket("T002", "WiFi slow", "Network", "medium", "in_progress", "Ana")
        self.assertEqual(
            format_result_line(ticket),
            "T002 | WiFi slow | Network | medium | in_progress | Ana",
        )

    def test_unassigned_ticket_shows_unassigned(self):
        ticket = make_ticket("T001", "Wifi down", "Network", "high", "open")
        self.assertTrue(format_result_line(ticket).endswith("| unassigned"))


if __name__ == "__main__":
    unittest.main()