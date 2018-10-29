from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class PaymentReasonValidator(object):
    @staticmethod
    def validate(payment_for):
        """Specifies which validation methods should be called for each input field.


        parameters:
            - payment_for: The reason for payment e.g. LON or official search

        returns:
            dict: A validation errors dict with the fieldname as a key and the associated validation errors in a list
            as the value.
        """

        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(payment_for, 'payment_for', 'Payment link reason', validation_error_builder,
                       inline_message='Choose one option') \
            .is_required()

        validation_errors = validation_error_builder.get()

        return validation_errors
