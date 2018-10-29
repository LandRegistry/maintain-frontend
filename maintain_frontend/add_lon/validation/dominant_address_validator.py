from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class DominantAddressValidator(object):

    @staticmethod
    def validate(form):
        """Extracts postcode and land description for validation.


        parameters:
            - form: The form which includes Yes/No radio buttons, postcode, and land description

        returns:
            dict: An instance of ValidationErrorBuilder with a ValidationError dict and a heading summary message.
        """

        have_address = form.get('have_address', '')
        charge_geographic_description = form.get('charge_geographic_description', '')

        validation_error_builder = ValidationErrorBuilder()

        if have_address == 'No':
            FieldValidator(charge_geographic_description, 'charge_geographic_description', None,
                           validation_error_builder,
                           summary_message='Location is required',
                           inline_message='Location is required') \
                .is_required()

        return validation_error_builder.get()
