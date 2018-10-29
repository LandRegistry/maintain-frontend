from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class ReferenceValidator(object):
    @staticmethod
    def validate(search_reference):
        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(search_reference, 'search-reference', None,
                       validation_error_builder,
                       summary_message="Authority reference or HM Land Registry reference is required") \
            .is_required()

        validation_errors = validation_error_builder.get()

        return validation_errors
