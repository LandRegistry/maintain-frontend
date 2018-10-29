from unittest import TestCase
from unittest.mock import patch, call
from maintain_frontend.add_land_charge.validation.location_confirmation_validator import LocationConfirmationValidator


class TestLocationConfirmationValidator(TestCase):

    @patch('maintain_frontend.add_land_charge.validation.location_confirmation_validator.ValidationErrorBuilder')
    @patch('maintain_frontend.add_land_charge.validation.location_confirmation_validator.FieldValidator')
    def test_params_passed_when_action_is_add(self, mock_field_validator, mock_error_builder):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        LocationConfirmationValidator.validate(True, 'add')

        calls = [
            call(True, 'location-confirmation', None, mock_error_builder(),
                 summary_message='Confirm that you have the authority to add this charge',
                 inline_message='If the charge is in your authority, tick and continue. '
                                'If the charge is in another authority, get permission from that authority.'),
            call().is_required()
        ]
        mock_field_validator.assert_has_calls(calls)

    @patch('maintain_frontend.add_land_charge.validation.location_confirmation_validator.ValidationErrorBuilder')
    @patch('maintain_frontend.add_land_charge.validation.location_confirmation_validator.FieldValidator')
    def test_params_passed(self, mock_field_validator, mock_error_builder):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        LocationConfirmationValidator.validate(True, 'vary')

        calls = [
            call(True, 'location-confirmation', None, mock_error_builder(),
                 summary_message='Confirm that you have the authority to update this charge',
                 inline_message='If the charge is in your authority, tick and continue. '
                                'If the charge is in another authority, get permission from that authority.'),
            call().is_required()
        ]
        mock_field_validator.assert_has_calls(calls)

    def test_validation_failed_when_input_is_blank_and_action_is_add(self):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        result = LocationConfirmationValidator.validate('', 'add')
        self.assertEqual(1, len(result.errors))

    def test_validation_failed_when_input_is_blank_and_action_is_vary(self):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        result = LocationConfirmationValidator.validate('', 'vary')
        self.assertEqual(1, len(result.errors))

    def test_validation_passes_with_valid_input_and_action_is_add(self):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        result = LocationConfirmationValidator.validate(True, 'add')
        self.assertEqual(0, len(result.errors))

    def test_validation_passes_with_valid_input_and_action_is_vary(self):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        result = LocationConfirmationValidator.validate(True, 'vary')
        self.assertEqual(0, len(result.errors))
