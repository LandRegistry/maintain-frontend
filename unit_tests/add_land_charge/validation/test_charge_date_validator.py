from unittest import TestCase
from unittest.mock import patch, call
from maintain_frontend.add_land_charge.validation.charge_date_validator import ChargeDateValidator

FIELD_NAME = 'date'
DISPLAY_NAME = 'Date'

CHARGE_DAY = ['some day']
CHARGE_MONTH = ['some month']
CHARGE_YEAR = ['some year']


class TestChargeDateValidator(TestCase):

    @patch('maintain_frontend.add_land_charge.validation.charge_date_validator.ValidationErrorBuilder')
    @patch('maintain_frontend.add_land_charge.validation.charge_date_validator.FieldsetValidator')
    def test_params_passed(self, mock_fieldset_validator, mock_error_builder):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        ChargeDateValidator.validate(CHARGE_DAY, CHARGE_MONTH, CHARGE_YEAR)

        calls = [
            call([CHARGE_DAY, CHARGE_MONTH, CHARGE_YEAR], FIELD_NAME, DISPLAY_NAME, mock_error_builder()),
            call().is_valid_date(),
            call([CHARGE_DAY, CHARGE_MONTH, CHARGE_YEAR], FIELD_NAME, DISPLAY_NAME, mock_error_builder(),
                 inline_message='Date cannot be a future date', summary_message='Date is invalid'),
            call().is_past_date()
        ]
        mock_fieldset_validator.assert_has_calls(calls)
