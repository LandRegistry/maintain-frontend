from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class LandCompensationTypeValidator(object):

    @staticmethod
    def validate(advance_payment_known):
        """Specifies which validation methods should be called for each input field.


        parameters:
            - advance_payment_known: Is the amount of advance payment known

        returns:
            dict: An instance of ValidationErrorBuilder with a ValidationError dict and a heading summary message.
        """

        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(advance_payment_known, 'advance-payment-known', 'Advance payment amount known',
                       validation_error_builder, summary_message='Choose one option',
                       inline_message='Choose one option') \
            .is_required()

        return validation_error_builder.get()
