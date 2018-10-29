from maintain_frontend.dependencies.session_api.last_created_charge import LastCreatedCharge
from unittest import TestCase


class TestLastCreatedCharge(TestCase):

    def test_state_initialisation(self):
        state = LastCreatedCharge()

        state.charge_id = 1
        state.entry_number = 2
        state.registration_date = "abc"

        self.assertIsNotNone(state)
        self.assertEqual(state.charge_id, 1)
        self.assertEqual(state.entry_number, 2)
        self.assertEqual(state.registration_date, "abc")

    def test_state_from_dict(self):

        test = dict()
        test["charge_id"] = 1
        test["entry_number"] = 2
        test["registration_date"] = "abc"

        state = LastCreatedCharge.from_dict(test)

        self.assertIsNotNone(state)
        self.assertEqual(state.charge_id, 1)
        self.assertEqual(state.entry_number, 2)
        self.assertEqual(state.registration_date, "abc")
