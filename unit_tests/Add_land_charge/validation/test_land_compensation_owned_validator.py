from unittest import TestCase
from unittest.mock import patch, call
from maintain_frontend.add_land_charge.validation.land_compensation_owned_validator \
    import LandCompensationOwnedValidator


class TestLandCompensationOwnedValidator(TestCase):

    @patch('maintain_frontend.add_land_charge.validation.land_compensation_owned_validator.ValidationErrorBuilder')
    @patch('maintain_frontend.add_land_charge.validation.land_compensation_owned_validator.FieldValidator')
    def test_min_params_passed(self, mock_field_validator, mock_error_builder):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        land_owned_indicator = 'Freehold'

        LandCompensationOwnedValidator.validate(land_owned_indicator, '')

        calls = [
            call(land_owned_indicator, 'land-owned-indicator', 'Land Owned Type', mock_error_builder(),
                 summary_message='Choose one option',
                 inline_message='This is the landowner\'s title to the land (how they own it).'),
            call().is_required()
        ]
        mock_field_validator.assert_has_calls(calls)

    @patch('maintain_frontend.add_land_charge.validation.land_compensation_owned_validator.ValidationErrorBuilder')
    @patch('maintain_frontend.add_land_charge.validation.land_compensation_owned_validator.FieldValidator')
    def test_max_params_passed(self, mock_field_validator, mock_error_builder):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        land_owned_indicator = 'Other'
        land_owned_other = 'Some text'

        LandCompensationOwnedValidator.validate(land_owned_indicator, land_owned_other)

        calls = [
            call(land_owned_indicator, 'land-owned-indicator', 'Land Owned Type', mock_error_builder(),
                 summary_message='Choose one option',
                 inline_message='This is the landowner\'s title to the land (how they own it).'),
            call().is_required(),

            call(land_owned_other, 'land-owned-other', 'Description of how the land is owned', mock_error_builder(),
                 summary_message='Describe how the land is owned',
                 inline_message='For example, in possession of the lender'),
            call().is_required(),

            call(land_owned_other, 'land-owned-other', 'Description of how the land is owned',
                 mock_error_builder(), summary_message="Answer too long",
                 inline_message="Answer must be shorter than 400 characters (about 60 words)"),
            call().is_length_less_than_or_equal_to(400)
        ]
        mock_field_validator.assert_has_calls(calls)

    def test_validation_failed_when_radio_input_is_blank(self):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        result = LandCompensationOwnedValidator.validate('', '')
        self.assertEqual(1, len(result.errors))
        self.assertEqual('Choose one option', result.errors['land-owned-indicator'].summary_message)

    def test_validation_failed_when_text_field_is_blank(self):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        result = LandCompensationOwnedValidator.validate('Other', '')
        self.assertEqual(1, len(result.errors))
        self.assertEqual('Describe how the land is owned',
                         result.errors['land-owned-other'].summary_message)

    def test_validation_failed_when_text_field_is_too_long(self):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        result = LandCompensationOwnedValidator.validate('Other', 'A' * 401)
        self.assertEqual(1, len(result.errors))
        self.assertEqual('Answer too long', result.errors['land-owned-other'].summary_message)

    def test_validation_passes_with_valid_input(self):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        land_owned_indicator = 'Other'
        land_owned_other = 'Some text'

        result = LandCompensationOwnedValidator.validate(land_owned_indicator, land_owned_other)
        self.assertEqual(0, len(result.errors))
