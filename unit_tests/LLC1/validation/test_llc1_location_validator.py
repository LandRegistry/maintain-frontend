from unittest import TestCase
from maintain_frontend.llc1.validation.location_validator import LocationValidator

VALID_LOCATION = 'Exeter'
INVALID_LOCATION = ''


class TestLLC1LocationValidator(TestCase):
    def test_location_supplied_passed(self):
        result = LocationValidator.validate(VALID_LOCATION).errors
        self.assertEqual(len(result), 0)

    def test_location_not_suppled_fails(self):
        result = LocationValidator.validate(INVALID_LOCATION).errors
        self.assertEqual(len(result), 1)
        self.assertEqual(result['location'].inline_message, "Enter an address")
        self.assertEqual(result['location'].summary_message, "Address is required")
