"""A fieldset validator to be used by specific validator classes."""
from maintain_frontend.services.validation.common_validator import CommonValidator


class FieldsetValidator(object):
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
    """
    def __init__(self, data, field_name, display_name, validation_error_builder,
                 inline_message=None, summary_message=None, explanatory_text=None, summary_heading_text=None):
        self.data = data
        self.field_name = field_name
        self.display_name = display_name
        self.inline_message = inline_message
        self.summary_message = summary_message
        self.explanatory_text = explanatory_text
        self.summary_heading_text = summary_heading_text
        self.validation_error_builder = validation_error_builder

    def is_required(self):
        default_message = '{} is required'.format(self.display_name)

        if not self.data:
            self.validation_error_builder.add_error(self, default_message)

        return self

    def has_enough_fields_populated(self, no_of_fields):
        """Checks if a sufficient number of fields are populated in the dataset."""
        populated_field_count = 0
        for field in self.data:
            if CommonValidator.is_required(field):
                populated_field_count += 1

        default_message = 'At least {} of {} is required'.format(str(no_of_fields), self.display_name)

        if populated_field_count < no_of_fields:
            self.validation_error_builder.add_error(self, default_message)

        return self

    def is_valid_date(self):
        """Checks if the array of day, month and year strings represents a valid date."""
        default_message = '{} is invalid'.format(self.display_name)

        if not CommonValidator.is_valid_date(self.data):
            self.validation_error_builder.add_error(self, default_message)

        return self

    def is_past_date(self):
        """Checks if the array of day, month and year strings represents a date in the past or the current date."""
        day = self.data[0]
        month = self.data[1]
        year = self.data[2]

        default_message = '{} was not the current date or in the past'.format(self.display_name)

        if not CommonValidator.is_past_date(day, month, year):
            self.validation_error_builder.add_error(self, default_message)

        return self

    def is_past_or_present_date(self):
        """Checks if the array of day, month and year strings represents a date in the past or the current date."""
        day = self.data[0]
        month = self.data[1]
        year = self.data[2]

        default_message = '{} was not the current date or in the past'.format(self.display_name)

        if not CommonValidator.is_past_or_present_date(day, month, year):
            self.validation_error_builder.add_error(self, default_message)

        return self

    def is_future_date(self):
        """Checks if the array of day, month and year strings represents a date in the future."""
        day = self.data[0]
        month = self.data[1]
        year = self.data[2]

        default_message = '{} was not the current date or in the past'.format(self.display_name)

        if not CommonValidator.is_future_date(day, month, year):
            self.validation_error_builder.add_error(self, default_message)

        return self

    def is_later_than_date(self, date):
        """Checks if the array of day, month and year strings represents a date later than another."""
        day = self.data[0]
        month = self.data[1]
        year = self.data[2]

        own_date = CommonValidator.build_date(day, month, year)
        other_date = CommonValidator.build_date(date[0], date[1], date[2])

        default_message = '{} was not later than date'.format(self.display_name)

        if not CommonValidator.is_later_than_date(own_date, other_date):
            self.validation_error_builder.add_error(self, default_message)

        return self
