from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.fieldset_validator import FieldsetValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class VaryLonValidator(object):
    @staticmethod
    def validate(form, files):
        form_b_name = "Form B"
        court_order_name = "Court Order"
        definitive_certificate_name = "Definitive Certificate"

        validation_error_builder = ValidationErrorBuilder()

        """ Form Fields """
        # Selected Certificates
        vary_lon_options = form.getlist('vary-lon-options')
        # Date of Definitive Certificate
        definitive_cert_day = form.get('definitive_cert_day')
        definitive_cert_month = form.get('definitive_cert_month')
        definitive_cert_year = form.get('definitive_cert_year')
        tribunal_definitive_certificate_date = [definitive_cert_day, definitive_cert_month, definitive_cert_year]

        """ Files """
        definitive_certificate = files.get('definitive-certificate-file-input')
        form_b = files.get('form-b-file-input')
        court_order = files.get('court-order-file-input')

        FieldValidator(vary_lon_options, 'vary-lon-options', None, validation_error_builder,
                       summary_message='Choose one option', inline_message='Choose one option') \
            .is_required()

        if definitive_certificate_name in vary_lon_options:
            FieldsetValidator(tribunal_definitive_certificate_date, 'tribunal_definitive_certificate_date',
                              None, validation_error_builder,
                              summary_message='Date is invalid',
                              inline_message='Check that the date is in Day/Month/Year format') \
                .is_valid_date()

            FieldsetValidator(tribunal_definitive_certificate_date, 'tribunal_definitive_certificate_date',
                              None, validation_error_builder,
                              summary_message='Date is invalid',
                              inline_message='Date cannot be a future date') \
                .is_past_or_present_date()

            FieldValidator(definitive_certificate, 'definitive-certificate-file-input', 'Definitive Certificate',
                           validation_error_builder,
                           inline_message="Upload a document for Definitive Certificate",
                           summary_message="Upload a document for Definitive Certificate") \
                .is_required()

            FieldValidator(definitive_certificate, 'definitive-certificate-file-input', "Definitive Certificate",
                           validation_error_builder,
                           inline_message='Upload a different file type. Accepted file formats are: pdf',
                           summary_message="File not recognised") \
                .is_pdf()

        if form_b_name in vary_lon_options:
            FieldValidator(form_b, 'form-b-file-input', 'Form B',
                           validation_error_builder,
                           inline_message="Upload a document for Form B",
                           summary_message="Upload a document for Form B") \
                .is_required()

            FieldValidator(form_b, 'form-b-cancel-lon-file-input', "Form B",
                           validation_error_builder,
                           inline_message='Upload a different file type. Accepted file formats are: pdf',
                           summary_message="File not recognised") \
                .is_pdf()

        if court_order_name in vary_lon_options:
            FieldValidator(court_order, 'court-order-file-input', "Court Order",
                           validation_error_builder,
                           inline_message="Upload a document for Court Order",
                           summary_message="Upload a document for Court Order") \
                .is_required()

            FieldValidator(court_order, 'court-order-file-input', "Court Order",
                           validation_error_builder,
                           inline_message='Upload a different file type. Accepted file formats are: pdf',
                           summary_message="File not recognised") \
                .is_pdf()

        return validation_error_builder.get()
