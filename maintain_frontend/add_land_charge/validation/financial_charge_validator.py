from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class FinancialChargeValidator(object):

    @staticmethod
    def validate(amount_known_indicator):
        """Specifies which validation methods should be called for each input field.


        parameters:
            - amount_known_indicator: If the amount secured is known.

        returns:
            dict: An instance of ValidationErrorBuilder with a ValidationError dict and a heading summary message.
        """

        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(amount_known_indicator, 'amount-known-indicator', 'Amount known', validation_error_builder,
                       summary_message='Choose one option', inline_message='Choose one option') \
            .is_required()

        return validation_error_builder.get()
