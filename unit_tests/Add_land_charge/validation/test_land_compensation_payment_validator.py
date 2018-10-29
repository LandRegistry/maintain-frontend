from unittest import TestCase
from unittest.mock import patch, call
from maintain_frontend.add_land_charge.validation.land_compensation_payment_validator \
    import LandCompensationPaymentValidator


class TestLandCompensationPaymentValidator(TestCase):

    @patch('maintain_frontend.add_land_charge.validation.land_compensation_payment_validator.ValidationErrorBuilder')
    @patch('maintain_frontend.add_land_charge.validation.land_compensation_payment_validator.FieldValidator')
    def test_params_passed(self, mock_field_validator, mock_error_builder):
        """should pass the given parameter to the fieldset validator and call the expected validations"""

        land_compensation_paid = '100'
        amount_of_compensation = '900'

        LandCompensationPaymentValidator.validate(land_compensation_paid, amount_of_compensation, False)

        calls = [
            call(land_compensation_paid, 'land-compensation-paid', 'Advance payment amount',
                 mock_error_builder(), summary_message='Enter the advance payment',
                 inline_message='This is part of the compensation (paid in advance)'),
            call().is_required(),

            call(amount_of_compensation, 'amount-of-compensation', 'Total compensation amount',
                 mock_error_builder(), summary_message='Enter the total compensation',
                 inline_message='This is the total compensation'),
            call().is_required(),

            call(amount_of_compensation, 'amount-of-compensation', 'Total compensation amount',
                 mock_error_builder(), summary_message='Compensation must be a positive number',
                 inline_message='Compensation must be a positive number'),
            call().is_positive_number(),

            call(land_compensation_paid, 'land-compensation-paid', 'Advance payment amount',
                 mock_error_builder(), summary_message='Advance payment cannot be more than total compensation',
                 inline_message='Advance payment cannot be more than total compensation'),
            call().is_less_than_or_equal_to(amount_of_compensation),

            call(amount_of_compensation, 'amount-of-compensation', 'Total compensation amount', mock_error_builder(),
                 summary_message='Compensation payment can only have 2 numbers after the decimal place',
                 inline_message='Compensation payment can only have 2 numbers after the decimal place'),
            call().is_number_with_zero_or_x_decimal_places(2),

            call(land_compensation_paid, 'land-compensation-paid', 'Advance payment amount',
                 mock_error_builder(), summary_message='Advance payment must be a positive number',
                 inline_message='Advance payment must be a positive number'),
            call().is_positive_number(),

            call(land_compensation_paid, 'land-compensation-paid', 'Advance payment amount', mock_error_builder(),
                 summary_message='Advance payment can only have 2 numbers after the decimal place',
                 inline_message='Advance payment can only have 2 numbers after the decimal place'),
            call().is_number_with_zero_or_x_decimal_places(2)
        ]
        mock_field_validator.assert_has_calls(calls)

    def test_validation_failed_when_input_is_blank(self):
        result = LandCompensationPaymentValidator.validate('', '', False)
        self.assertEqual(2, len(result.errors))
        self.assertEqual('Enter the advance payment', result.errors['land-compensation-paid'].summary_message)
        self.assertEqual('Enter the total compensation', result.errors['amount-of-compensation'].summary_message)
        self.assertEqual('This is part of the compensation (paid in advance)',
                         result.errors['land-compensation-paid'].inline_message)
        self.assertEqual('This is the total compensation', result.errors['amount-of-compensation'].inline_message)

    def test_validation_failed_when_amount_field_contains_pound_symbol(self):
        result = LandCompensationPaymentValidator.validate('£123.45', '900', False)
        self.assertEqual(1, len(result.errors))
        self.assertEqual('Advance payment must be a positive number',
                         result.errors['land-compensation-paid'].summary_message)

    def test_validation_failed_when_amount_fields_are_invalid(self):
        result = LandCompensationPaymentValidator.validate('abcdefg', 'defghijk', False)
        self.assertEqual(2, len(result.errors))
        self.assertEqual('Advance payment must be a positive number',
                         result.errors['land-compensation-paid'].summary_message)
        self.assertEqual('Compensation must be a positive number',
                         result.errors['amount-of-compensation'].summary_message)
        self.assertEqual('Advance payment must be a positive number',
                         result.errors['land-compensation-paid'].inline_message)
        self.assertEqual('Compensation must be a positive number',
                         result.errors['amount-of-compensation'].inline_message)

    def test_validation_failed_when_advance_higher_than_total(self):
        result = LandCompensationPaymentValidator.validate('300', '100', False)
        self.assertEqual(1, len(result.errors))
        self.assertEqual('Advance payment cannot be more than total compensation',
                         result.errors['land-compensation-paid'].summary_message)
        self.assertEqual('Advance payment cannot be more than total compensation',
                         result.errors['land-compensation-paid'].inline_message)

    def test_validation_failed_when_amount_fields_are_more_than_2dp(self):
        result = LandCompensationPaymentValidator.validate('1.999', '2.999', False)
        self.assertEqual(2, len(result.errors))
        self.assertEqual('Advance payment can only have 2 numbers after the decimal place',
                         result.errors['land-compensation-paid'].summary_message)
        self.assertEqual('Compensation payment can only have 2 numbers after the decimal place',
                         result.errors['amount-of-compensation'].summary_message)
        self.assertEqual('Advance payment can only have 2 numbers after the decimal place',
                         result.errors['land-compensation-paid'].inline_message)
        self.assertEqual('Compensation payment can only have 2 numbers after the decimal place',
                         result.errors['amount-of-compensation'].inline_message)

    def test_validation_passes_with_valid_input(self):
        land_compensation_paid = '100'
        amount_of_compensation = '900'

        result = LandCompensationPaymentValidator.validate(land_compensation_paid, amount_of_compensation, False)
        self.assertEqual(0, len(result.errors))

    def test_validation_passes_with_blank_amount_type(self):
        land_compensation_paid = '100'
        amount_of_compensation = '900'

        result = LandCompensationPaymentValidator.validate(land_compensation_paid, amount_of_compensation, False)
        self.assertEqual(0, len(result.errors))

    def test_validation_passes_with_blank_amount_of_compensation_when_varying(self):
        land_compensation_paid = '100'
        amount_of_compensation = ''

        result = LandCompensationPaymentValidator.validate(land_compensation_paid, amount_of_compensation, True)
        self.assertEqual(0, len(result.errors))
