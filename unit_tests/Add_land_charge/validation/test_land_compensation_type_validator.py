from unittest import TestCase
from unittest.mock import patch, call
from maintain_frontend.add_land_charge.validation.land_compensation_type_validator import LandCompensationTypeValidator


class TestLandCompensationTypeValidator(TestCase):

    @patch('maintain_frontend.add_land_charge.validation.land_compensation_type_validator.ValidationErrorBuilder')
    @patch('maintain_frontend.add_land_charge.validation.land_compensation_type_validator.FieldValidator')
    def test_params_passed(self, mock_field_validator, mock_error_builder):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        LandCompensationTypeValidator.validate('Yes')

        calls = [
            call('Yes', 'advance-payment-known', 'Advance payment amount known', mock_error_builder(),
                 summary_message='Choose one option', inline_message='Choose one option'),
            call().is_required()
        ]
        mock_field_validator.assert_has_calls(calls)

    def test_validation_failed_when_input_is_blank(self):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        result = LandCompensationTypeValidator.validate('')
        self.assertEqual(1, len(result.errors))

    def test_validation_passes_with_valid_input(self):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        result = LandCompensationTypeValidator.validate('Yes')
        self.assertEqual(0, len(result.errors))
