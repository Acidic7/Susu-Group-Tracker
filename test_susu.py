import unittest
from decimal import Decimal

from susu import SusuGroup


class SusuGroupTests(unittest.TestCase):
    def setUp(self):
        self.group = SusuGroup("50.00")
        for name in ("Ama", "Kofi", "Esi"):
            self.group.add_member(name)

    def test_partial_payment_and_balance(self):
        self.group.record_contribution("Esi", "30.00")
        self.assertEqual(self.group.amount_paid("Esi"), Decimal("30.00"))
        self.assertEqual(self.group.amount_owed("Esi"), Decimal("20.00"))

    def test_week_cannot_close_if_member_owes(self):
        self.group.record_contribution("Ama", "50.00")
        self.group.record_contribution("Kofi", "50.00")
        self.group.record_contribution("Esi", "30.00")
        message = self.group.close_week()
        self.assertIn("cannot close", message)
        self.assertIn("Esi owes GHS 20.00", message)
        self.assertEqual(self.group.current_week, 1)
        self.assertEqual(self.group.payout_history, [])

    def test_complete_week_pays_first_member_and_advances(self):
        for name in ("Ama", "Kofi", "Esi"):
            self.group.record_contribution(name, "50.00")
        message = self.group.close_week()
        self.assertIn("Ama receives GHS 150.00", message)
        self.assertEqual(self.group.current_week, 2)
        self.assertEqual(self.group.payout_history[0].recipient, "Ama")
        self.assertEqual(self.group.payout_history[0].amount, Decimal("150.00"))

    def test_next_week_pays_next_member(self):
        for _ in range(2):
            for name in ("Ama", "Kofi", "Esi"):
                self.group.record_contribution(name, "50.00")
            self.group.close_week()
        self.assertEqual(self.group.payout_history[1].recipient, "Kofi")
        self.assertEqual(self.group.payout_history[1].week, 2)

    def test_rejects_duplicate_member_case_insensitively(self):
        with self.assertRaises(ValueError):
            self.group.add_member("ama")

    def test_rejects_unknown_member(self):
        with self.assertRaises(ValueError):
            self.group.record_contribution("Yaw", "10.00")

    def test_rejects_zero_negative_and_overpayment(self):
        for amount in ("0", "-1", "50.01"):
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError):
                    self.group.record_contribution("Ama", amount)

    def test_rejects_add_member_after_week_starts(self):
        self.group.record_contribution("Ama", "10.00")
        with self.assertRaises(ValueError):
            self.group.add_member("Yaw")

    def test_rejects_fractional_pesewa(self):
        with self.assertRaises(ValueError):
            self.group.record_contribution("Ama", "10.001")


if __name__ == "__main__":
    unittest.main()
