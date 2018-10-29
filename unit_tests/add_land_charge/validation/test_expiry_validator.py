from unittest import TestCase
from unittest.mock import patch, call
from maintain_frontend.add_land_charge.validation.expiry_validator import ExpiryValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder

VALIDATION_PATH = 'maintain_frontend.add_land_charge.validation'
validationErrorBuilder = ValidationErrorBuilder()

CHARGE_EXPIRED = 'yes'
CHARGE_NOT_EXPIRED = 'no'

DATE_INVALID = 'Date is invalid'
DATE_YEAR_FORMAT_MESSAGE = 'Year must be in the format YYYY'


class TestExpiryValidator(TestCase):
    @patch('{}.expiry_validator.ValidationErrorBuilder'.format(VALIDATION_PATH))
    @patch('{}.expiry_validator.FieldValidator'.format(VALIDATION_PATH))
    def test_does_charge_expire_not_provided(self, mock_field_validator, mock_validation_error_builder):
        mock_validation_error_builder.return_value = validationErrorBuilder
        does_charge_expire = ''
        ExpiryValidator.validate(does_charge_expire, '', '', '')

        calls = [
            call(does_charge_expire, 'does_charge_expire', None, validationErrorBuilder,
                 summary_message='Choose one option',
                 inline_message='Choose \'No\' if you don’t have this information.'),
            call().is_required()
        ]
        mock_field_validator.assert_has_calls(calls)

    @patch('{}.expiry_validator.ValidationErrorBuilder'.format(VALIDATION_PATH))
    @patch('{}.expiry_validator.FieldValidator'.format(VALIDATION_PATH))
    def test_charge_does_not_expire_should_not_require_other_fields(
        self,
        mock_field_validator,
        mock_validation_error_builder
    ):
        mock_validation_error_builder.return_value = validationErrorBuilder
        does_charge_expire = 'no'
        ExpiryValidator.validate(does_charge_expire, '', '', '')

        calls = [
            call(does_charge_expire, 'does_charge_expire', None, validationErrorBuilder,
                 summary_message='Choose one option',
                 inline_message='Choose \'No\' if you don’t have this information.'),
            call().is_required()
        ]
        mock_field_validator.assert_has_calls(calls)

    def test_charge_does_expire_should_require_other_fields(self):
        result = ExpiryValidator.validate(CHARGE_EXPIRED, '', '', '').errors
        self.assertIsNotNone(result)
        self.assertEqual(
            result['charge_expiry_date'].summary_message,
            'Enter an expiry date'
        )

    @patch('{}.expiry_validator.ValidationErrorBuilder'.format(VALIDATION_PATH))
    @patch('{}.expiry_validator.FieldsetValidator'.format(VALIDATION_PATH))
    def test_valid_date_if_provided(self, mock_fieldset_validator, mock_validation_error_builder):
        mock_validation_error_builder.return_value = validationErrorBuilder
        does_charge_expire = 'yes'
        charge_expiry_day = '12'
        charge_expiry_month = '12'
        charge_expiry_year = '2020'

        ExpiryValidator.validate(
            does_charge_expire,
            charge_expiry_day,
            charge_expiry_month,
            charge_expiry_year
        )

        charge_expiry_date = [charge_expiry_day, charge_expiry_month, charge_expiry_year]

        calls = [
            call(charge_expiry_date, 'charge_expiry_date', 'Date', validationErrorBuilder),
            call().is_valid_date()
        ]
        mock_fieldset_validator.assert_has_calls(calls)

    def test_date_year_1_digit(self):
        result = ExpiryValidator.validate(CHARGE_EXPIRED, '1', '1', '1').errors
        self.assertIsNotNone(result)
        self.assertEqual(result['charge_expiry_date'].summary_message, DATE_INVALID)
        self.assertEqual(result['charge_expiry_date'].inline_message, DATE_YEAR_FORMAT_MESSAGE)

    def test_date_year_2_digits(self):
        result = ExpiryValidator.validate(CHARGE_EXPIRED, '1', '1', '01').errors
        self.assertIsNotNone(result)
        self.assertEqual(result['charge_expiry_date'].summary_message, DATE_INVALID)
        self.assertEqual(result['charge_expiry_date'].inline_message, DATE_YEAR_FORMAT_MESSAGE)

    def test_date_year_3_digits(self):
        result = ExpiryValidator.validate(CHARGE_EXPIRED, '1', '1', '001').errors
        self.assertIsNotNone(result)
        self.assertEqual(result['charge_expiry_date'].summary_message, DATE_INVALID)
        self.assertEqual(result['charge_expiry_date'].inline_message, DATE_YEAR_FORMAT_MESSAGE)

    def test_date_year_4_digits(self):
        result = ExpiryValidator.validate(CHARGE_EXPIRED, '1', '1', '0001').errors
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 0)
