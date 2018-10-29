from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class LocationConfirmationValidator(object):
    @staticmethod
    def validate(confirmation, action):
        """Specifies which validation methods should be called for each input FieldValidator.


        parameters:
            - confirmation: Whether the user acknowledges they are permitted to add the charge.

        returns:
            dict: An instance of ValidationErrorBuilder with a ValidationError dict and a heading summary message.
        """

        validation_error_builder = ValidationErrorBuilder()

        if action == 'update':
            summary_message_text = 'Confirm that you have the authority to update this charge'
        elif action == 'cancel':
            summary_message_text = 'Confirm that you have the authority to cancel this charge'

        FieldValidator(confirmation, 'location-confirmation', None, validation_error_builder,
                       summary_message=summary_message_text,
                       inline_message='If the charge is in your authority, tick and continue. '
                                      'If the charge is in another authority, get permission from that authority.') \
            .is_required()

        return validation_error_builder.get()
