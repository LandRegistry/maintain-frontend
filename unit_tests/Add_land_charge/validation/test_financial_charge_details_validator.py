from unittest import TestCase
from unittest.mock import patch, call
from maintain_frontend.add_land_charge.validation.financial_charge_details_validator \
    import FinancialChargeDetailsValidator


class TestFinancialChargeDetailsValidator(TestCase):

    @patch('maintain_frontend.add_land_charge.validation.financial_charge_details_validator.ValidationErrorBuilder')
    @patch('maintain_frontend.add_land_charge.validation.financial_charge_details_validator.FieldValidator')
    def test_min_params_passed(self, mock_field_validator, mock_error_builder):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        amount_secured = '100'
        interest_paid_indicator = 'No'

        FinancialChargeDetailsValidator.validate(amount_secured, interest_paid_indicator, '')

        calls = [
            call(amount_secured, 'amount-secured', 'Amount originally secured', mock_error_builder(),
                 summary_message='Amount is required',
                 inline_message="If you don't know the amount, go back and choose 'No'"),
            call().is_required(),

            call(amount_secured, 'amount-secured', 'Amount originally secured', mock_error_builder(),
                 summary_message='Amount must be a positive number with up to 2 decimal places',
                 inline_message='Amount must be a positive number with up to 2 decimal places, for example '
                                '100 or 100.10'),
            call().is_number_with_zero_or_x_decimal_places(2),

            call(amount_secured, 'amount-secured', 'Amount originally secured', mock_error_builder(),
                 summary_message='Amount cannot have more than 13 characters before the decimal point',
                 inline_message='Amount must be shorter than 13 characters'),
            call().is_number_x_length_y_decimal_places(13, 2),

            call(interest_paid_indicator, 'interest-paid-indicator', 'Interest paid', mock_error_builder(),
                 summary_message='Choose one option', inline_message='Choose one option'),
            call().is_required()
        ]
        mock_field_validator.assert_has_calls(calls)

    @patch('maintain_frontend.add_land_charge.validation.financial_charge_details_validator.ValidationErrorBuilder')
    @patch('maintain_frontend.add_land_charge.validation.financial_charge_details_validator.FieldValidator')
    def test_max_params_passed(self, mock_field_validator, mock_error_builder):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        amount_secured = '100'
        interest_paid_indicator = 'Yes'
        interest_rate = '5.1'

        FinancialChargeDetailsValidator.validate(amount_secured, interest_paid_indicator, interest_rate)

        calls = [
            call(amount_secured, 'amount-secured', 'Amount originally secured', mock_error_builder(),
                 summary_message='Amount is required',
                 inline_message="If you don't know the amount, go back and choose 'No'"),
            call().is_required(),

            call(amount_secured, 'amount-secured', 'Amount originally secured', mock_error_builder(),
                 summary_message='Amount must be a positive number with up to 2 decimal places',
                 inline_message='Amount must be a positive number with up to 2 decimal places, for example '
                                '100 or 100.10'),
            call().is_number_with_zero_or_x_decimal_places(2),

            call(amount_secured, 'amount-secured', 'Amount originally secured', mock_error_builder(),
                 summary_message='Amount cannot have more than 13 characters before the decimal point',
                 inline_message='Amount must be shorter than 13 characters'),
            call().is_number_x_length_y_decimal_places(13, 2),

            call(interest_paid_indicator, 'interest-paid-indicator', 'Interest paid', mock_error_builder(),
                 summary_message='Choose one option', inline_message='Choose one option'),
            call().is_required(),

            call(interest_rate, 'interest-rate', 'Interest rate', mock_error_builder(),
                 summary_message='Interest is required',
                 inline_message='Interest is the authority\'s borrowing rate or other agreed rate'),
            call().is_required(),

            call(interest_rate, 'interest-rate', 'Interest rate', mock_error_builder(),
                 summary_message='Interest rate cannot have more than 70 characters',
                 inline_message='Interest rate must be shorter than 70 characters'),
            call().is_length_less_than_or_equal_to(70)
        ]
        mock_field_validator.assert_has_calls(calls)

    def test_validation_failed_when_input_is_blank(self):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        result = FinancialChargeDetailsValidator.validate('', '', '')
        self.assertEqual(2, len(result.errors))
        self.assertEqual('Amount is required', result.errors['amount-secured'].summary_message)
        self.assertEqual('Choose one option', result.errors['interest-paid-indicator'].summary_message)

    def test_validation_failed_when_two_text_fields_are_blank(self):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        result = FinancialChargeDetailsValidator.validate('', 'Yes', '')
        self.assertEqual(2, len(result.errors))
        self.assertEqual('Amount is required', result.errors['amount-secured'].summary_message)
        self.assertEqual('Interest is required', result.errors['interest-rate'].summary_message)

    def test_validation_failed_when_two_text_fields_are_invalid(self):
        """should pass the given parameter to the fieldset validator and call the expected validations"""
        rate = ""
        for x in range(0, 71):
            rate = rate + "a"
        result = FinancialChargeDetailsValidator.validate('123.4', 'Yes', rate)
        self.assertEqual(2, len(result.errors))
        self.assertEqual('Amount must be a positive number with up to 2 decimal places',
                         result.errors['amount-secured'].summary_message)
        self.assertEqual('Interest rate cannot have more than 70 characters',
                         result.errors['interest-rate'].summary_message)

    def test_validation_passes_with_valid_input(self):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        amount_secured = '100.00'
        interest_paid_indicator = 'Yes'
        interest_rate = '5.1'

        result = FinancialChargeDetailsValidator.validate(amount_secured, interest_paid_indicator, interest_rate)
        self.assertEqual(0, len(result.errors))
