from unittest import TestCase

from maintain_frontend.add_land_charge.validation.additional_info_validator \
    import AddChargeAdditionalInfoValidator

VALID_FI_LOCATION = 'a' * 500
INVALID_FI_LOCATION = VALID_FI_LOCATION + '!'
VALID_REFERENCE = 'a' * 255
INVALID_REFERENCE = VALID_REFERENCE + '!'


class TestAddChargeAdditionalInfoValidator(TestCase):

    def test_min_fields_populated_passed(self):
        result = AddChargeAdditionalInfoValidator.validate(VALID_FI_LOCATION, '').errors
        self.assertEqual(len(result), 0)

    def test_min_fields_populated_failed(self):
        result = AddChargeAdditionalInfoValidator.validate('', '').errors

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result['additional-info-error'].summary_message,
            'Add a department name and address, or a link to charge documents'
        )
        self.assertEqual(
            result['additional-info-error'].inline_message,
            'Add a source'
        )

    def test_additional_info_character_limit(self):
        result = AddChargeAdditionalInfoValidator.validate(INVALID_FI_LOCATION, '').errors

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result['additional-info-error'].summary_message,
            'Answer is too long'
        )
        self.assertEqual(
            result['additional-info-error'].inline_message,
            'Reduce your answer to 500 characters or less'
        )

    def test_reference_character_limit(self):
        result = AddChargeAdditionalInfoValidator.validate('a', INVALID_REFERENCE).errors

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result['reference'].summary_message,
            'Reference is too long'.format(INVALID_REFERENCE)
        )
        self.assertEqual(
            result['reference'].inline_message,
            'Reduce your answer to 255 characters or less'.format(INVALID_REFERENCE)
        )
