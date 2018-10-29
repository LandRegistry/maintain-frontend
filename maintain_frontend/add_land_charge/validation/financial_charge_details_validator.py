from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class FinancialChargeDetailsValidator(object):

    @staticmethod
    def validate(amount_secured, interest_paid_indicator, interest_rate):
        """Specifies which validation methods should be called for each input field.


        parameters:
            - amount_secured: The amount secured
            - interest_paid_indicator: Indicates if interest will be paid on the amount.
            - interest_rate: The interest rate.

        returns:
            dict: An instance of ValidationErrorBuilder with a ValidationError dict and a heading summary message.
        """

        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(amount_secured, 'amount-secured', 'Amount originally secured', validation_error_builder,
                       summary_message='Amount is required',
                       inline_message="If you don't know the amount, go back and choose 'No'").is_required()

        FieldValidator(amount_secured, 'amount-secured', 'Amount originally secured', validation_error_builder,
                       summary_message='Amount must be a positive number with up to 2 decimal places',
                       inline_message='Amount must be a positive number with up to 2 decimal places, for example '
                                      '100 or 100.10')\
            .is_number_with_zero_or_x_decimal_places(2)

        FieldValidator(amount_secured, 'amount-secured', 'Amount originally secured', validation_error_builder,
                       summary_message='Amount cannot have more than 13 characters before the decimal point',
                       inline_message='Amount must be shorter than 13 characters') \
            .is_number_x_length_y_decimal_places(13, 2)

        FieldValidator(interest_paid_indicator, 'interest-paid-indicator', 'Interest paid', validation_error_builder,
                       summary_message='Choose one option', inline_message='Choose one option').is_required()

        if interest_paid_indicator == 'Yes':

            FieldValidator(interest_rate, 'interest-rate', 'Interest rate', validation_error_builder,
                           summary_message='Interest is required',
                           inline_message="Interest is the authority's borrowing rate or other agreed rate")\
                .is_required()

            FieldValidator(interest_rate, 'interest-rate', 'Interest rate', validation_error_builder,
                           summary_message='Interest rate cannot have more than 70 characters',
                           inline_message='Interest rate must be shorter than 70 characters') \
                .is_length_less_than_or_equal_to(70)

        return validation_error_builder.get()
