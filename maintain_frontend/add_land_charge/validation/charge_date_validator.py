from maintain_frontend.services.validation.fieldset_validator import FieldsetValidator
from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class ChargeDateValidator(object):

    @staticmethod
    def validate(day, month, year):
        """Specifies which validation methods should be called for each input field.


        parameters:
            - day: The day the charge was added. This is an optional field on the form.
            - month: The month the charge was added. This is an optional field on the form.
            - year: The year the charge was added. This is an optional field on the form.

        returns:
            dict: An instance of ValidationErrorBuilder with a ValidationError dict and a heading summary message.
        """

        validation_error_builder = ValidationErrorBuilder()

        if day or month or year:
            FieldsetValidator([day, month, year], 'date', 'Date', validation_error_builder) \
                .is_valid_date()

            FieldValidator(year, "date", 'Date', validation_error_builder,
                           summary_message="Date is invalid", inline_message="Year must be in the format YYYY")\
                .is_year_format()

            FieldsetValidator([day, month, year], 'date', 'Date', validation_error_builder,
                              summary_message="Date is invalid", inline_message="Date cannot be a future date") \
                .is_past_date()

        return validation_error_builder.get()
