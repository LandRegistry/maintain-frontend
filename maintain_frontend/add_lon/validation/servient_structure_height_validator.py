from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class ServientStructureHeightValidator(object):

    @staticmethod
    def validate(measurement, height, unit):
        specific_height = "I have measurements for the height"

        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(measurement, 'measurement', None, validation_error_builder,
                       summary_message='Choose one option',
                       inline_message='Check the paperwork. Usually this is \'Unlimited height\' '
                                      'but you may be given exact measurements')\
            .is_required()

        if measurement == specific_height:
            FieldValidator(height, 'height', None, validation_error_builder,
                           summary_message='Enter a height',
                           inline_message='This can be \'unlimited height\' or a specific measurement') \
                .is_required()

            FieldValidator(unit, 'unit', None, validation_error_builder,
                           summary_message='Enter a measurement',
                           inline_message='This is usually \'metres\' but check the dimensions on Form A') \
                .is_required()

        return validation_error_builder.get()
