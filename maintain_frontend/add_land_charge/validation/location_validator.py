from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class AddLocationMapValidator(object):
    @staticmethod
    def validate(geo_json, summary_error=None, inline_error=None):
        """Specifies which validation methods should be called for each input field.


        parameters:
            - role: role selected for user.

        returns:
            dict: An instance of ValidationErrorBuilder with a ValidationError dict and a heading summary message
        """

        validation_error_builder = ValidationErrorBuilder()

        features = []
        if geo_json is not None and "features" in geo_json:
            features = geo_json["features"]

        FieldValidator(features, 'map', 'Boundary', validation_error_builder,
                       summary_message=summary_error, inline_message=inline_error, allow_multiple=True) \
            .is_required()

        FieldValidator(features, 'map', 'Boundary', validation_error_builder,
                       summary_message='Delete boundary',
                       inline_message='Delete a boundary to continue',
                       explanatory_text='The maximum number of boundary lines is 500',
                       allow_multiple=True) \
            .is_item_count_no_greater_than(500)

        # Test each feature for errors
        for feature in features:
            error_count = 0
            if 'map' in validation_error_builder.errors:
                error_count = len(validation_error_builder.errors['map'])

            FieldValidator(feature, 'map', 'Boundary', validation_error_builder,
                           summary_message='Lines cannot be a point',
                           inline_message='Draw longer lines or use a different tool for your extents',
                           explanatory_text=None, allow_multiple=True) \
                .has_zero_length_line_geometry()

            FieldValidator(feature, 'map', 'Boundary', validation_error_builder,
                           summary_message='Polygons cannot be a point or line',
                           inline_message='Draw larger polygons or use a different tool to draw your extents',
                           explanatory_text=None, allow_multiple=True) \
                .has_zero_area_polygon_geometry()

            # Zero length lines/polys also evaluate as invalid/simple, prefer the above and skip below checks
            if 'map' in validation_error_builder.errors and error_count < len(validation_error_builder.errors['map']):
                continue

            FieldValidator(feature, 'map', 'Boundary', validation_error_builder,
                           summary_message='Extents cannot include a loop',
                           inline_message='Remove any loops or knots in the polygons',
                           explanatory_text=None, allow_multiple=True) \
                .has_simple_geometry()

            # Polygon loops only detected by is_valid
            FieldValidator(feature, 'map', 'Boundary', validation_error_builder,
                           summary_message='Extents cannot include a loop',
                           inline_message='Remove any loops or knots in the polygons',
                           explanatory_text=None, allow_multiple=True) \
                .has_valid_geometry()

        return validation_error_builder.get()
