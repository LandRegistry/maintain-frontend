from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class PaymentMethodValidator(object):

    @staticmethod
    def validate(form):
        """Extracts value from common fields from applicant info and address_fields_partial for validation.


        parameters:
            - form: The form which includes the payment methods

        returns:
            dict: An instance of ValidationErrorBuilder with a ValidationError dict and a heading summary message.
        """

        payment_method = form.get('payment_method', '')
        payment_ref = form.get('payment_ref', '')
        no_payment_notes = form.get('no_payment_notes', '')

        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(payment_method, 'payment_method', 'Payment method', validation_error_builder,
                       inline_message='Choose one option') \
            .is_required()

        if payment_method == "govuk":
            FieldValidator(payment_ref, 'payment_ref', 'Payment reference', validation_error_builder) \
                .is_required()

        if payment_method == "none":
            FieldValidator(no_payment_notes, 'no_payment_notes', 'Explanation', validation_error_builder) \
                .is_required()

        return validation_error_builder.get()
