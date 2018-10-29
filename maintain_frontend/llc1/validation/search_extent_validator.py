from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class SearchExtentValidator(object):
    @staticmethod
    def validate(geo_json):
        """Specifies which validation methods should be called for each input field.


        parameters:
            - role: role selected for user.

        returns:
            dict: An instance of ValidationErrorBuilder with a ValidationError dict and a heading summary message
        """

        validation_error_builder = ValidationErrorBuilder()

        features = None
        if geo_json is not None and "features" in geo_json:
            features = geo_json["features"]

        FieldValidator(features, 'map', 'Boundary', validation_error_builder,
                       summary_message='Draw the extent',
                       inline_message='Extent is required') \
            .is_required()

        return validation_error_builder.get()
