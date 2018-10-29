from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class AuthorityValidator(object):

    @staticmethod
    def validate(authority, authorities):
        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(authority, 'authority-search-field', 'Originating Authority', validation_error_builder,
                       summary_message='Authority name is required', inline_message='Authority name is required') \
            .is_required()

        FieldValidator(authority, 'authority-search-field', 'Originating Authority', validation_error_builder,
                       summary_message='No match found', inline_message='Try a different search') \
            .is_item_in_list(authorities)

        return validation_error_builder.get()
