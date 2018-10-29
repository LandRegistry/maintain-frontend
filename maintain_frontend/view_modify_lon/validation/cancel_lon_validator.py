from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class CancelLonValidator(object):
    @staticmethod
    def validate(form, files):
        form_b_name = "Form B"
        court_order_name = "Court Order"

        validation_error_builder = ValidationErrorBuilder()

        """ Form Fields """
        # Selected Certificates
        cancel_options = form.getlist('cancel-options')

        """ Files """
        form_b = files.get('form-b-cancel-lon-file-input')
        court_order = files.get('court-order-cancel-lon-file-input')

        FieldValidator(cancel_options, 'cancel-options', None, validation_error_builder,
                       summary_message='Choose one option', inline_message='Choose one option') \
            .is_required()

        if form_b_name in cancel_options:
            FieldValidator(form_b, 'form-b-cancel-lon-file-input', 'Form B',
                           validation_error_builder,
                           inline_message="Upload a document for Form B",
                           summary_message="Upload a document for Form B") \
                .is_required()

            FieldValidator(form_b, 'form-b-cancel-lon-file-input', "Form B",
                           validation_error_builder,
                           inline_message='Upload a different file type. Accepted file formats are: pdf',
                           summary_message="File not recognised") \
                .is_pdf()

        if court_order_name in cancel_options:
            FieldValidator(court_order, 'court-order-cancel-lon-file-input', "Court Order",
                           validation_error_builder,
                           inline_message="Upload a document for Court Order",
                           summary_message="Upload a document for Court Order") \
                .is_required()

            FieldValidator(court_order, 'court-order-cancel-lon-file-input', "Court Order",
                           validation_error_builder,
                           inline_message='Upload a different file type. Accepted file formats are: pdf',
                           summary_message="File not recognised") \
                .is_pdf()

        return validation_error_builder.get()
