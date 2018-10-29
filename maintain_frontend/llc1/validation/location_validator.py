from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class LocationValidator(object):
    @staticmethod
    def validate(location_info):
        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(location_info, 'location', None,
                       validation_error_builder,
                       summary_message="Address is required",
                       inline_message="Enter an address") \
            .is_required()

        validation_errors = validation_error_builder.get()

        return validation_errors
