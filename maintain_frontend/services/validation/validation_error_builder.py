from collections import OrderedDict
from maintain_frontend.services.validation.validation_error import ValidationError


class ValidationErrorBuilder(object):
    """A class to build a dict containing error messages in the form:


    {
        errors: {
            field_name: {
                summary_message (message to display in the summary box at head of page, which often links to an input),
                inline_message (message to display above the input)
                explanatory_text
            }
        },
        summary_heading_text (the heading to use in the error summary box)
    }

    Alternatively field_name can map to an array of errors for fields that require multiple errors (geometry)
    """

    def __init__(self):
        self.errors = OrderedDict()
        self.summary_heading_text = 'There are errors on this page'

    def add_error(self, validator, default_message, allow_multiple=False):
        """Adds an error for a field name that is added to an OrderedDict of errors.


        - validator: A validator whose fields will be used to construct the error message.
        - default_message: The error message to append if a heading or summary message is not provided.
        """

        # Only add this error message if there is not already one for this field and not allowing multiple
        if validator.field_name in self.errors and not allow_multiple:
            return

        error = ValidationError()

        #  Set the heading text for the summary box.
        if validator.summary_heading_text is not None:
            self.summary_heading_text = validator.summary_heading_text

        #  Set the summary message.
        if validator.summary_message is not None:
            error.summary_message = validator.summary_message
        else:
            error.summary_message = default_message

        #  Set the explanatory text.
        if validator.explanatory_text is not None:
            error.explanatory_text = validator.explanatory_text

        # Set the inline message.
        if validator.inline_message is not None:
            error.inline_message = validator.inline_message
        else:
            error.inline_message = default_message

        # If allowing multiple do things differently
        if allow_multiple:
            if validator.field_name not in self.errors:
                self.errors[validator.field_name] = []
            # Prevent duplicate errors
            for curr_error in self.errors[validator.field_name]:
                if curr_error.summary_message == error.summary_message and \
                        curr_error.explanatory_text == error.explanatory_text and \
                        curr_error.inline_message == error.inline_message:
                    return
            self.errors[validator.field_name].append(error)
        else:
            # Add the error to the dictionary.
            self.errors[validator.field_name] = error

    def get(self):
        return self
