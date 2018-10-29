from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class LegalDocumentValidator(object):

    @staticmethod
    def validate(instrument):
        """Specifies which validation methods should be called for each input field.


        parameters:
            - instrument: The instrument of the charge being added.

        returns:
            dict: An instance of ValidationErrorBuilder with a ValidationError dict and a heading summary message.
        """

        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(instrument, 'confirm-instruments', 'Legal document', validation_error_builder,
                       summary_message='Choose one option', inline_message='Choose one option') \
            .is_required()

        return validation_error_builder.get()
