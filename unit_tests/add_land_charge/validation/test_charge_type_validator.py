from unittest import TestCase
from unittest.mock import patch, call
from maintain_frontend.add_land_charge.validation.charge_type_validator import ChargeTypeValidator

CHARGE_TYPE = 'test charge type'


class TestChargeTypeValidator(TestCase):

    @patch('maintain_frontend.add_land_charge.validation.charge_type_validator.ValidationErrorBuilder')
    @patch('maintain_frontend.add_land_charge.validation.charge_type_validator.FieldValidator')
    def test_params_passed(self, mock_field_validator, mock_error_builder):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        ChargeTypeValidator.validate(CHARGE_TYPE)

        calls = [
            call(CHARGE_TYPE, 'charge-type', 'Charge type', mock_error_builder(),
                 summary_message='Choose one option', inline_message='Choose one option'),
            call().is_required()
        ]
        mock_field_validator.assert_has_calls(calls)
