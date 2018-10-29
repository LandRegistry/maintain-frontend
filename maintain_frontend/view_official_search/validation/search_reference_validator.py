from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class SearchReferenceValidator(object):
    @staticmethod
    def validate(reference, found=True):
        """Specifies which validation methods should be called for each input field.


        parameters:
            - reference: Search reference

        returns:
            dict: A validation errors dict with the fieldname as a key and the associated validation errors in a list
            as the value.
        """

        validation_error_builder = ValidationErrorBuilder()

        if found:
            FieldValidator(reference, 'search_reference', 'Reference', validation_error_builder,
                           inline_message='Enter a search reference',
                           summary_message='Enter a search reference') \
                .is_required()

            FieldValidator(reference, 'search_reference', 'Reference', validation_error_builder,
                           inline_message='Search reference must only include numbers 0 to 9',
                           summary_message='Search reference must only include numbers 0 to 9') \
                .is_positive_number_or_zero().is_length_less_than_or_equal_to(9)

            FieldValidator(reference, 'search_reference', 'Reference', validation_error_builder) \
                .is_int()
        else:
            FieldValidator('', 'search_reference', 'Reference', validation_error_builder,
                           inline_message='Search reference does not exist',
                           summary_message='Search reference does not exist') \
                .is_required()

        validation_errors = validation_error_builder.get()

        return validation_errors
