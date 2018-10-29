from unittest import TestCase
from unittest.mock import patch, call
from maintain_frontend.add_land_charge.validation.land_compensation_land_sold_validator \
    import LandCompensationLandSoldValidator

VALID_LAND_SOLD = 'some land sold description'
VALID_WORK_DONE = 'some work particulars'
INVALID_FIELD_LENGTH = 'a' * 401


class TestLandCompensationLandSoldValidator(TestCase):

    @patch('maintain_frontend.add_land_charge.validation.land_compensation_land_sold_validator.ValidationErrorBuilder')
    @patch('maintain_frontend.add_land_charge.validation.land_compensation_land_sold_validator.FieldValidator')
    def test_validation_called(self, mock_field_validator, mock_error_builder):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        LandCompensationLandSoldValidator.validate(VALID_LAND_SOLD, VALID_WORK_DONE)

        calls = [
            call(VALID_LAND_SOLD, 'land-sold-description', 'Description of the charge', mock_error_builder(),
                 summary_message='Describe the land sold',
                 inline_message='This is the land bought by the authority, so they can do public works on the land.'),
            call().is_required(),

            call(VALID_LAND_SOLD, 'land-sold-description', 'Description of the charge',
                 mock_error_builder(), summary_message="Answer too long",
                 inline_message="Answer must be shorter than 400 characters (about 60 words)"),
            call().is_length_less_than_or_equal_to(400),

            call(VALID_WORK_DONE, 'land-works-particulars', 'The description of the work planned',
                 mock_error_builder(), summary_message='Describe the work',
                 inline_message='This is the work that the authority wants to do on the land they have bought.'),
            call().is_required(),

            call(VALID_WORK_DONE, 'land-works-particulars', 'The description of the work planned',
                 mock_error_builder(), summary_message="Answer too long",
                 inline_message="Answer must be shorter than 400 characters (about 60 words)"),
            call().is_length_less_than_or_equal_to(400)
        ]
        mock_field_validator.assert_has_calls(calls)

    def test_validation_failed_when_input_is_blank(self):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        result = LandCompensationLandSoldValidator.validate('', '')
        self.assertEqual(2, len(result.errors))
        self.assertEqual('Describe the land sold', result.errors['land-sold-description'].summary_message)
        self.assertEqual('Describe the work', result.errors['land-works-particulars'].summary_message)

    def test_validation_fails_with_invalid_field_length(self):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        result = LandCompensationLandSoldValidator.validate(INVALID_FIELD_LENGTH, INVALID_FIELD_LENGTH)
        self.assertEqual(2, len(result.errors))
        self.assertEqual('Answer too long', result.errors['land-sold-description'].summary_message)
        self.assertEqual('Answer too long', result.errors['land-works-particulars'].summary_message)

    def test_validation_passes_with_valid_input(self):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        result = LandCompensationLandSoldValidator.validate(VALID_LAND_SOLD, VALID_WORK_DONE)
        self.assertEqual(0, len(result.errors))
