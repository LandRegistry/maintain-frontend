from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class LandCompensationOwnedValidator(object):

    @staticmethod
    def validate(land_owned_indicator, land_owned_other):
        """Specifies which validation methods should be called for each input field.


        parameters:
            - land_owned_indicator: Indicates how the land is owned.
            - land_owned_other: More details if the land_owned_indicator is 'Other'.

        returns:
            dict: An instance of ValidationErrorBuilder with a ValidationError dict and a heading summary message.
        """

        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(land_owned_indicator, 'land-owned-indicator', 'Land Owned Type', validation_error_builder,
                       summary_message='Choose one option',
                       inline_message='This is the landowner\'s title to the land (how they own it).').is_required()

        if land_owned_indicator == 'Other':

            FieldValidator(land_owned_other, 'land-owned-other', 'Description of how the land is owned',
                           validation_error_builder,
                           summary_message='Describe how the land is owned',
                           inline_message='For example, in possession of the lender') \
                .is_required()

            FieldValidator(land_owned_other, 'land-owned-other', 'Description of how the land is owned',
                           validation_error_builder, summary_message="Answer too long",
                           inline_message="Answer must be shorter than 400 characters (about 60 words)") \
                .is_length_less_than_or_equal_to(400)

        return validation_error_builder.get()
