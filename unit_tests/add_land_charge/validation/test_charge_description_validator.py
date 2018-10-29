
from unittest import TestCase
from maintain_frontend.add_land_charge.validation.charge_description_validator import ChargeDescriptionValidator

VALID_CHARGE_DESCRIPTION = 'some charge description'
INVALID_CHARGE_DESCRIPTION_LENGTH = 'a' * 1501


class TestChargeReasonValidator(TestCase):

    def test_valid(self):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        result = ChargeDescriptionValidator.validate(VALID_CHARGE_DESCRIPTION).errors
        self.assertEqual(len(result), 0)

    def test_invalid_length(self):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        result = ChargeDescriptionValidator.validate(INVALID_CHARGE_DESCRIPTION_LENGTH).errors

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result['charge-description'].summary_message,
            'Answer too long'
        )
        self.assertEqual(
            result['charge-description'].inline_message,
            'Reduce your answer to 1500 characters or fewer'
        )
