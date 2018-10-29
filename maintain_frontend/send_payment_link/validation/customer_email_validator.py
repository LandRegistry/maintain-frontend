from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class CustomerEmailValidator(object):
    @staticmethod
    def validate(email):
        """Specifies which validation methods should be called for each input field.


        parameters:
            - email: Customer's email

        returns:
            dict: A validation errors dict with the fieldname as a key and the associated validation errors in a list
            as the value.
        """

        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(email, 'email', 'Email', validation_error_builder) \
            .is_required()

        FieldValidator(email, 'email', email, validation_error_builder) \
            .is_email()

        validation_errors = validation_error_builder.get()

        return validation_errors
