import unittest

from campusflow.validation import (
    parse_affected_users,
    validate_affected_users,
    validate_category,
    validate_staff_name,
    validate_status,
    validate_ticket_id,
    validate_title,
    validate_urgency,
)


class TestValidators(unittest.TestCase):

    def test_title_is_trimmed(self):
        self.assertEqual(validate_title("  Wi-Fi down  "), "Wi-Fi down")

    def test_blank_or_non_text_title_rejected(self):
        for bad in ["", "   ", None, 5]:
            with self.assertRaises(ValueError):
                validate_title(bad)

    def test_category_is_normalised(self):
        self.assertEqual(validate_category("  network "), "Network")

    def test_invalid_category_rejected(self):
        for bad in ["Plumbing", "", None]:
            with self.assertRaises(ValueError):
                validate_category(bad)

    def test_urgency_is_normalised(self):
        self.assertEqual(validate_urgency(" HIGH "), "high")

    def test_invalid_urgency_rejected(self):
        for bad in ["urgent", "", None]:
            with self.assertRaises(ValueError):
                validate_urgency(bad)

    def test_affected_users_rejects_bad_values(self):
        for bad in [0, -1, 2.5, "5", True, False, None]:
            with self.assertRaises(ValueError):
                validate_affected_users(bad)

    def test_affected_users_accepts_positive_int(self):
        self.assertEqual(validate_affected_users(7), 7)

    def test_parse_affected_users_accepts_digits(self):
        self.assertEqual(parse_affected_users(" 12 "), 12)

    def test_parse_affected_users_rejects_bad_text(self):
        for bad in ["", "abc", "2.5", "-3", "0", "1e3", "\u0663"]:
            with self.assertRaises(ValueError):
                parse_affected_users(bad)

    def test_staff_name_is_trimmed_and_blank_rejected(self):
        self.assertEqual(validate_staff_name("  Ada "), "Ada")
        for bad in ["", "   ", None]:
            with self.assertRaises(ValueError):
                validate_staff_name(bad)

    def test_ticket_id_is_normalised(self):
        self.assertEqual(validate_ticket_id(" t001 "), "T001")

    def test_bad_ticket_id_rejected(self):
        for bad in ["", "001", "TABC", "T", 5, None]:
            with self.assertRaises(ValueError):
                validate_ticket_id(bad)

    def test_status_validation(self):
        self.assertEqual(validate_status(" In_Progress "), "in_progress")
        with self.assertRaises(ValueError):
            validate_status("done")


if __name__ == "__main__":
    unittest.main()