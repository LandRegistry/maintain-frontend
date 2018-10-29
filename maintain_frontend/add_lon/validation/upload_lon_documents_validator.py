from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.fieldset_validator import FieldsetValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder
from maintain_frontend.services.validation.common_validator import CommonValidator


class UploadLonDocumentsValidator(object):
    @staticmethod
    def validate(form, files):
        definitive_cert = "Definitive LON certificate"
        temporary_cert = "Temporary LON certificate"

        validation_error_builder = ValidationErrorBuilder()

        """ Form Fields """
        # Selected Certificates
        certificates = form.getlist('certificate')
        # Date of Temporary Certificate
        temp_cert_day = form.get('temp_cert_day')
        temp_cert_month = form.get('temp_cert_month')
        temp_cert_year = form.get('temp_cert_year')
        tribunal_temporary_certificate_date = [temp_cert_day, temp_cert_month, temp_cert_year]
        # Expiry of Temporary Certificate
        temp_expiry_day = form.get('temp_expiry_day')
        temp_expiry_month = form.get('temp_expiry_month')
        temp_expiry_year = form.get('temp_expiry_year')
        # Date of Definitive Certificate
        definitive_cert_day = form.get('definitive_cert_day')
        definitive_cert_month = form.get('definitive_cert_month')
        definitive_cert_year = form.get('definitive_cert_year')
        tribunal_definitive_certificate_date = [definitive_cert_day, definitive_cert_month, definitive_cert_year]

        """ Files """
        form_a = files.get('form-a-file-input')
        definitive_certificate = files.get('definitive-lon-cert-file-input')
        temporary_certificate = files.get('temporary-lon-cert-file-input')

        FieldValidator(certificates, 'certificate', None, validation_error_builder,
                       summary_message='Choose one option', inline_message='Choose one option') \
            .is_required()

        if definitive_cert in certificates:
            FieldsetValidator(tribunal_definitive_certificate_date, 'tribunal_definitive_certificate_date',
                              None, validation_error_builder,
                              summary_message='Date is invalid (certificate date, definitive certificate)',
                              inline_message='Check that the date is in Day/Month/Year format') \
                .is_valid_date()

            FieldsetValidator(tribunal_definitive_certificate_date, 'tribunal_definitive_certificate_date',
                              None, validation_error_builder,
                              summary_message='Date is invalid (certificate date, definitive certificate)',
                              inline_message='Date cannot be a future date') \
                .is_past_or_present_date()

            FieldValidator(definitive_certificate, 'definitive-lon-cert-file-input', 'Definitive Certificate',
                           validation_error_builder,
                           inline_message="Upload a document for Definitive LON certificate",
                           summary_message="Upload a document for Definitive LON certificate") \
                .is_required()

            FieldValidator(definitive_certificate, 'definitive-lon-cert-file-input', "Definitive Certificate",
                           validation_error_builder,
                           inline_message='Upload a different file type. Accepted file formats are: pdf',
                           summary_message="File not recognised") \
                .is_pdf()

        if temporary_cert in certificates:
            FieldsetValidator(tribunal_temporary_certificate_date, 'tribunal_temporary_certificate_date',
                              None, validation_error_builder,
                              summary_message='Date is invalid (certificate date, temporary certificate)',
                              inline_message='Check that the date is in Day/Month/Year format') \
                .is_valid_date()

            FieldsetValidator(tribunal_temporary_certificate_date, 'tribunal_temporary_certificate_date',
                              None, validation_error_builder,
                              summary_message='Date is invalid (certificate date, temporary certificate)',
                              inline_message='Date cannot be a future date') \
                .is_past_or_present_date()

            tribunal_temporary_certificate_expiry_date = [temp_expiry_day, temp_expiry_month, temp_expiry_year]
            FieldsetValidator(tribunal_temporary_certificate_expiry_date, 'tribunal_temporary_certificate_expiry_date',
                              None, validation_error_builder,
                              summary_message='Date is invalid (expiry date, temporary certificate)',
                              inline_message='Check that the date is in Day/Month/Year format') \
                .is_valid_date()

            FieldValidator(temporary_certificate, 'temporary-lon-cert-file-input', "Temporary Certificate",
                           validation_error_builder,
                           inline_message="Upload a document for Temporary LON certificate",
                           summary_message="Upload a document for Temporary LON certificate") \
                .is_required()

            FieldValidator(temporary_certificate, 'temporary-lon-cert-file-input', "Temporary Certificate",
                           validation_error_builder,
                           inline_message='Upload a different file type. Accepted file formats are: pdf',
                           summary_message="File not recognised") \
                .is_pdf()

        if definitive_cert in certificates and temporary_cert in certificates:
            compare_definitive_and_temporary_dates(tribunal_definitive_certificate_date,
                                                   tribunal_temporary_certificate_date,
                                                   validation_error_builder)

        FieldValidator(form_a, 'form-a-file-input', 'form_a', validation_error_builder,
                       inline_message="Upload a file for Plan A and colour plan",
                       summary_message="Upload a file for Plan A and colour plan") \
            .is_required()

        FieldValidator(form_a, 'form-a-file-input', 'form_a', validation_error_builder,
                       inline_message='Upload a different file type. Accepted file formats are: pdf',
                       summary_message="File not recognised") \
            .is_pdf()

        return validation_error_builder.get()


def compare_definitive_and_temporary_dates(definitive_date, temporary_date, error_builder):
    if CommonValidator.is_valid_date(definitive_date) and CommonValidator.is_valid_date(temporary_date):
        FieldsetValidator(definitive_date, 'tribunal_definitive_certificate_date',
                          None, error_builder,
                          summary_message='Date (definitive certificate) must come '
                                          'after date (temporary certificate).',
                          inline_message='Date (definitive certificate) must come '
                                         'after date (temporary certificate).')\
            .is_later_than_date(temporary_date)
