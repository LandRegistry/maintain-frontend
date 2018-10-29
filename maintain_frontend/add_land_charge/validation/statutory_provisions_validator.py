from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class StatutoryProvisionsValidator(object):

    @staticmethod
    def validate(law, provision_list=None):
        """Specifies which validation methods should be called for each input field.


        parameters:
            - law: The law of the charge being added.
            - provision_list: List to valid statutory permissions

        returns:
            dict: An instance of ValidationErrorBuilder with a ValidationError dict and a heading summary message.
        """

        validation_error_builder = ValidationErrorBuilder()

        if provision_list is None:
            FieldValidator(law, 'confirm-law', 'Law', validation_error_builder,
                           summary_message='Choose one option', inline_message='Choose one option') \
                .is_required()

        if provision_list is not None:
            FieldValidator(law, 'legislation', 'Law', validation_error_builder) \
                .is_required().is_item_in_list(provision_list)

        return validation_error_builder.get()
