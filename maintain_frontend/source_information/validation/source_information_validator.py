from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class SourceInformationValidator(object):
    @staticmethod
    def validate(source_info):
        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(source_info, 'source-information', None,
                       validation_error_builder,
                       summary_message="Enter a source",
                       inline_message="Enter a source") \
            .is_required()

        FieldValidator(source_info, 'source-information', None,
                       validation_error_builder,
                       summary_message='Answer too long',
                       inline_message='Reduce your answer to 500 characters or less') \
            .is_length_less_than_or_equal_to(500)

        validation_errors = validation_error_builder.get()

        return validation_errors
