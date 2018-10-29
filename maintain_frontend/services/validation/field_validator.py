"""A form validator used to validate individual inputs on a page returning a dictionary of errors for display."""
from maintain_frontend.services.validation.common_validator import CommonValidator


class FieldValidator(object):
    """Checks for validation errors and calls validation_error_builder to construct error messages.


    parameters:
        - data: The input data to be validated.
        - field_name: The name of the field that has an error. This should match the name property of the form input,
                      and the id of the label to link to from the error message box.
        - display_name: The display friendly name of the field. Used by the default error messages. Pass None here if
                        providing a custom summary_message and inline_message.
        - validation_error_builder: A class to build an ordered dictionary or error messages in the form:
                                    {
                                        errors: {
                                            field_name: {
                                                summary_message (message to display in the summary box at head of page,
                                                                 which often links to an input),
                                                inline_message (message to display above the input)
                                            }
                                        },
                                        summary_heading_text (the heading to use in the error summary box)
                                    }
        - inline_message (Optional): The message to be displayed inline above the input. If not provided a default
                                     message will be used.
        - summary_message (Optional): The message to be displayed in the error summary at the head of the page. If not
                                      provided a default message will be used.
        - explanatory_text (Optional): The message will be displayed in the error summary, below the summary_message.
        - summary_heading_text (Optional): Text to display as the heading for the error summary box.
        - allow_multiple (Optional): Whether the field should be allowed multiple errors.
    """

    def __init__(self, data, field_name, display_name, validation_error_builder,
                 inline_message=None, summary_message=None, explanatory_text=None, summary_heading_text=None,
                 allow_multiple=False):
        self.data = data
        self.field_name = field_name
        self.display_name = display_name
        self.inline_message = inline_message
        self.summary_message = summary_message
        self.explanatory_text = explanatory_text
        self.summary_heading_text = summary_heading_text
        self.validation_error_builder = validation_error_builder
        self.allow_multiple = allow_multiple

    def is_required(self):
        """Checks if the data provided is not empty."""
        default_message = '{} is required'.format(self.display_name)

        if not CommonValidator.is_required(self.data):
            self.validation_error_builder.add_error(self, default_message, self.allow_multiple)

        return self

    def is_email(self):
        """Checks if the data provided is a valid email format."""
        default_message = '{} is not a valid email address'.format(self.display_name)

        if self.data and not CommonValidator.is_email(self.data):
            self.validation_error_builder.add_error(self, default_message, self.allow_multiple)

        return self

    def is_year_format(self):
        """Checks if a year field contains the required format (YYYY)"""
        default_message = '{} must be in the format YYYY'.format(self.display_name)

        if self.data and not len(str(self.data)) == 4:
            self.validation_error_builder.add_error(self, default_message, self.allow_multiple)

        return self

    def is_length_less_than_or_equal_to(self, length):
        """Checks if the data provided is less than or equal to a specified length."""
        default_message = '{} is greater than {} characters'.format(self.display_name, str(length))

        if self.data and not CommonValidator.is_length_less_than_or_equal_to(self.data, length):
            self.validation_error_builder.add_error(self, default_message, self.allow_multiple)

        return self

    def is_length_equal_to(self, length):
        """Checks if the data provided is equal to a specified length."""
        default_message = '{} is not {} characters'.format(self.display_name, str(length))

        if self.data and not CommonValidator.is_length_equal_to(self.data, length):
            self.validation_error_builder.add_error(self, default_message, self.allow_multiple)

        return self

    def is_phone_number(self):
        """Checks if the data provided is a valid phone number ie. all numeric, allow space."""
        default_message = '{} is not a valid phone number'.format(self.display_name)

        if self.data and not CommonValidator.is_phone_number(self.data):
            self.validation_error_builder.add_error(self, default_message, self.allow_multiple)

        return self

    def is_item_count_equal_to(self, length):
        """Checks if the data set provided has the correct length."""
        default_message = 'Only {} {} can be supplied'.format(length, self.display_name.lower())

        if self.data is not None:
            if not len(self.data) == length:
                self.validation_error_builder.add_error(self, default_message, self.allow_multiple)

        return self

    def is_item_count_no_greater_than(self, length):
        """Checks if the data set provided is less than maximum length."""
        default_message = 'Only less than {} {} can be supplied'.format(length, self.display_name.lower())

        if self.data is not None:
            if len(self.data) > length:
                self.validation_error_builder.add_error(self, default_message, self.allow_multiple)

        return self

    def is_item_in_list(self, valid_entries):
        """Checks if the item is in list."""
        default_message = '{} is not a valid selection for {}'.format(self.data, self.display_name.lower())

        if self.data is not None:
            if self.data.lower() not in (entry.lower() for entry in valid_entries):
                self.validation_error_builder.add_error(self, default_message, self.allow_multiple)

        return self

    def is_item_not_in_list(self, invalid_entries):
        """Checks if the item is not in list."""
        default_message = '{} is not a valid selection for {}'.format(self.data, self.display_name.lower())

        if self.data is not None:
            if self.data in invalid_entries:
                self.validation_error_builder.add_error(self, default_message, self.allow_multiple)

        return self

    def is_postcode(self):
        """Checks if the data provided is a valid postcode."""
        default_message = '{} is not a valid postcode'.format(self.display_name)

        if self.data and not CommonValidator.is_postcode(self.data):
            self.validation_error_builder.add_error(self, default_message, self.allow_multiple)

        return self

    def is_pdf(self):
        """Checks if the file provided is a pdf"""
        default_message = '{} is not a valid pdf'.format(self.display_name)

        if self.data and not CommonValidator.is_pdf(self.data.content_type):
            self.validation_error_builder.add_error(self, default_message, self.allow_multiple)

        return self

    def is_number_with_zero_or_x_decimal_places(self, decimal_places):
        """Checks if the data provided is a number with zero X decimal places."""
        default_message = '{} is not a valid number format'.format(self.display_name)

        if self.data and not CommonValidator.is_number_with_zero_or_x_decimal_places(self.data, decimal_places):
            self.validation_error_builder.add_error(self, default_message, self.allow_multiple)

        return self

    def is_number_with_zero_or_up_to_x_decimal_places(self, decimal_places):
        """Checks if the data provided is a number with zero X decimal places."""
        default_message = '{} is not a valid number format'.format(self.display_name)

        if self.data and not CommonValidator.is_number_with_zero_or_up_to_x_decimal_places(self.data, decimal_places):
            self.validation_error_builder.add_error(self, default_message, self.allow_multiple)

        return self

    def is_number_x_length_y_decimal_places(self, length, decimal_places):
        """Checks if the data provided is a number up to x characters long with exactly y decimal places."""
        default_message = '{} is not a valid number format'.format(self.display_name)

        if self.data and not CommonValidator.is_number_x_length_y_decimal_places(self.data, length, decimal_places):
            self.validation_error_builder.add_error(self, default_message, self.allow_multiple)

        return self

    def is_number_x_length_up_to_y_decimal_places(self, length, decimal_places):
        """Checks if the data provided is a number up to x characters long with exactly y decimal places."""
        default_message = '{} is not a valid number format'.format(self.display_name)

        if self.data and not CommonValidator.is_number_x_length_up_to_y_decimal_places(self.data,
                                                                                       length,
                                                                                       decimal_places):
            self.validation_error_builder.add_error(self, default_message, self.allow_multiple)

        return self

    def does_string_contain(self, character):
        default_message = '{} contains the character: {}'.format(self.display_name, character)

        if self.data and CommonValidator.does_string_contain(self.data, character):
            self.validation_error_builder.add_error(self, default_message, self.allow_multiple)

        return self

    def has_simple_geometry(self):
        """Checks that the geometry supplied is simple"""
        default_message = '{} contains geometry which is not simple'.format(self.display_name)

        if self.data and not CommonValidator.check_geometry(self.data, ['is_simple']):
            self.validation_error_builder.add_error(self, default_message, self.allow_multiple)

        return self

    def has_valid_geometry(self):
        """Checks that the geometry supplied is valid"""
        default_message = '{} contains geometry which is not valid'.format(self.display_name)

        if self.data and not CommonValidator.check_geometry(self.data, ['is_valid']):
            self.validation_error_builder.add_error(self, default_message, self.allow_multiple)

        return self

    def has_zero_length_line_geometry(self):
        """Checks that the geometry supplied has no zero length lines"""
        default_message = '{} contains line geometry which has zero length'.format(self.display_name)

        if self.data and not CommonValidator.check_geometry(self.data, ['zero_length']):
            self.validation_error_builder.add_error(self, default_message, self.allow_multiple)

        return self

    def has_zero_area_polygon_geometry(self):
        """Checks that the geometry supplied has no zero area polygons"""
        default_message = '{} contains polygon geometry which has zero area'.format(self.display_name)

        if self.data and not CommonValidator.check_geometry(self.data, ['zero_area']):
            self.validation_error_builder.add_error(self, default_message, self.allow_multiple)

        return self

    def is_uploaded_filesize_less_than_bytes(self, no_of_bytes):
        default_message = "File is too big"

        if self.data and not CommonValidator.is_uploaded_filesize_less_than_bytes(self.data, no_of_bytes):
            self.validation_error_builder.add_error(self, default_message, self.allow_multiple)

    def is_less_than_or_equal_to(self, number):
        default_message = 'First number must be less than or equal to second number'

        if self.data and self.__is_parsable(number) and self.__is_parsable(self.data):
            if float(self.data) > float(number):
                self.validation_error_builder.add_error(self, default_message, self.allow_multiple)

        return self

    def is_positive_number(self):
        default_message = 'Provided number must be a positive number'

        if not self.__is_parsable(self.data) or \
           (self.__is_parsable(self.data) and not CommonValidator.is_positive_number(self.data)):
                self.validation_error_builder.add_error(self, default_message, self.allow_multiple)
        return self

    def is_positive_number_or_zero(self):
        default_message = 'Provided number must be a positive number or zero'

        if not self.__is_parsable(self.data) or \
           (self.__is_parsable(self.data) and not CommonValidator.is_positive_number_or_zero(self.data)):
                self.validation_error_builder.add_error(self, default_message, self.allow_multiple)
        return self

    def is_int(self):
        default_message = 'Provided number must not have decimal places'

        if not CommonValidator.is_int(self.data):
            self.validation_error_builder.add_error(self, default_message, self.allow_multiple)
        return self

    def __is_parsable(self, value):
        try:
            float(value)
        except ValueError:
            return False
        return True
