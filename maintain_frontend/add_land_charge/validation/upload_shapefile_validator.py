import fiona
from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class UploadShapefileValidator(object):
    @staticmethod
    def validate(shapefile, existing_geometries, already_uploaded):
        """Specifies which validation methods should be called for each input field.


        parameters:
            - shapefile: The contents of the file the user has uploaded
            - existing_geometries: A collection of features already drawn/uploaded by the user
            - already_uploaded: True if user has clicked upload button multiple times and session has been updated

        returns:
            dict: An instance of ValidationErrorBuilder with a ValidationError dict and a heading summary message.
        """
        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(shapefile, 'shapefile-input', 'shapefile-input', validation_error_builder,
                       summary_message="Upload a file",
                       inline_message="Upload a file") \
            .is_required()

        FieldValidator(shapefile, 'shapefile-input', 'shapefile-input', validation_error_builder,
                       summary_message="File is bigger than 1MB",
                       inline_message="Upload a smaller file") \
            .is_uploaded_filesize_less_than_bytes(1000000)

        if already_uploaded:
            all_extents = existing_geometries['features'] \
                if existing_geometries and 'features' in existing_geometries \
                else []
        else:
            shapefile_contents = []

            try:
                with fiona.drivers():
                    with fiona.BytesCollection(shapefile.read()) as shpfile:
                        for shape in shpfile:
                            shapefile_contents.append(shape)
                shapefile.seek(0)
            except Exception:
                pass

            FieldValidator(shapefile_contents, 'shapefile-input', 'shapefile-input', validation_error_builder,
                           summary_message="File not uploaded",
                           inline_message="Upload a different file") \
                .is_required()

            if existing_geometries and 'features' in existing_geometries:
                all_extents = shapefile_contents + existing_geometries['features']
            else:
                all_extents = shapefile_contents

        FieldValidator(all_extents, 'shapefile-input', 'shapefile-input', validation_error_builder,
                       inline_message="Too many extents",
                       summary_message="Number of extents must be 500 (or fewer)") \
            .is_length_less_than_or_equal_to(500)

        return validation_error_builder.get()
