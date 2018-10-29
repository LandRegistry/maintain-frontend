from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class ChargeDescriptionValidator(object):

    @staticmethod
    def validate(charge_description):
        """Specifies which validation methods should be called for each input field.


        parameters:
            - charge_description: The description of a charge.

        returns:
            dict: An instance of ValidationErrorBuilder with a ValidationError dict and a heading summary message.
        """

        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(charge_description, 'charge-description', 'Description of the charge',
                       validation_error_builder,
                       inline_message="Reduce your answer to 1500 characters or fewer",
                       summary_message="Answer too long") \
            .is_length_less_than_or_equal_to(1500)

        return validation_error_builder.get()
