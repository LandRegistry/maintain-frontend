from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class AddChargeAdditionalInfoValidator(object):
    @staticmethod
    def validate(information, reference):
        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(information, 'additional-info-error', 'Additional Information', validation_error_builder,
                       summary_message="Answer is too long",
                       inline_message="Reduce your answer to 500 characters or less") \
            .is_length_less_than_or_equal_to(500)

        FieldValidator(information, 'additional-info-error', 'Additional Information', validation_error_builder,
                       summary_message="Add a department name and address, or a link to charge documents",
                       inline_message='Add a source') \
            .is_required()

        FieldValidator(reference, 'reference', 'Reference', validation_error_builder,
                       summary_message="Reference is too long",
                       inline_message="Reduce your answer to 255 characters or less") \
            .is_length_less_than_or_equal_to(255)

        return validation_error_builder.get()
