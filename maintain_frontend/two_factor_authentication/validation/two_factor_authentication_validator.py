from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class TwoFactorAuthenticationValidator(object):
    field_name = 'code'
    display_name = 'Security code'
    inline_message = None
    summary_message = None
    explanatory_text = None
    summary_heading_text = None

    @staticmethod
    def validate(code):
        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(code, 'code', 'Security code',
                       validation_error_builder,
                       summary_message="Invalid security code",
                       inline_message="Invalid security code") \
            .is_required() \
            .is_length_equal_to(5) \
            .is_positive_number()

        validation_errors = validation_error_builder.get()

        return validation_errors

    @staticmethod
    def generate_invalid_code_error_message():
        validation_error_builder = ValidationErrorBuilder()
        validation_error_builder.add_error(TwoFactorAuthenticationValidator, 'Invalid security code')
        validation_errors = validation_error_builder.get()

        return validation_errors
