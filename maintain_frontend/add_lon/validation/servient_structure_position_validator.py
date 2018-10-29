from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class ServientStructurePositionValidator(object):

    @staticmethod
    def validate(extent, part_extent_detail):
        part_extent_option = "Part of the extent"

        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(extent, 'extent', None, validation_error_builder,
                       summary_message='Choose one option',
                       inline_message='Check Plan A. This will show you which part of the structure will block '
                                      'light') \
            .is_required()

        if extent == part_extent_option:
            FieldValidator(part_extent_detail, 'part_extent_detail', None, validation_error_builder,
                           summary_message='Enter a description',
                           inline_message='Check Plan A. This will give you a written description of the servient '
                                          'land') \
                .is_required()

        return validation_error_builder.get()
