from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class LandCompensationLandSoldValidator(object):

    @staticmethod
    def validate(land_sold_description, land_works_particulars):
        """Specifies which validation methods should be called for each input field.


        parameters:
            - land_sold_description: The description of a charge.
            - land_works_particulars: The description of the work planned.
        returns:
            dict: An instance of ValidationErrorBuilder with a ValidationError dict and a heading summary message.
        """

        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(land_sold_description, 'land-sold-description', 'Description of the charge',
                       validation_error_builder,
                       inline_message='This is the land bought by the authority, '
                                      'so they can do public works on the land.',
                       summary_message="Describe the land sold") \
            .is_required()

        FieldValidator(land_sold_description, 'land-sold-description', 'Description of the charge',
                       validation_error_builder,
                       inline_message="Answer must be shorter than 400 characters (about 60 words)",
                       summary_message="Answer too long") \
            .is_length_less_than_or_equal_to(400)

        FieldValidator(land_works_particulars, 'land-works-particulars', 'The description of the work planned',
                       validation_error_builder,
                       inline_message="This is the work that the authority wants to do on the land they have bought.",
                       summary_message="Describe the work") \
            .is_required()

        FieldValidator(land_works_particulars, 'land-works-particulars', 'The description of the work planned',
                       validation_error_builder,
                       inline_message="Answer must be shorter than 400 characters (about 60 words)",
                       summary_message="Answer too long") \
            .is_length_less_than_or_equal_to(400)

        return validation_error_builder.get()
