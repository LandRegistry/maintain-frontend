from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class ApplicantInfoValidator(object):

    @staticmethod
    def validate(form):
        """Extracts value from common fields from applicant info and address_fields_partial for validation.


        parameters:
            - form: The form which includes the address_fields partial

        returns:
            dict: An instance of ValidationErrorBuilder with a ValidationError dict and a heading summary message.
        """

        applicant_name = form.get('applicant_name', '')
        address = form.get('address_line_1', '') + \
            form.get('address_line_2', '') + \
            form.get('address_line_3', '') + \
            form.get('address_line_4', '') + \
            form.get('address_line_5', '') + \
            form.get('address_line_6', '')
        country = form.get('country', '')
        postcode = form.get('postcode', '')

        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(applicant_name, 'applicant_name', 'Name', validation_error_builder) \
            .is_required()

        FieldValidator(applicant_name, 'applicant_name', 'Name', validation_error_builder,
                       "Reduce your answer to 200 characters or less", "Answer is too long") \
            .is_length_less_than_or_equal_to(200)

        FieldValidator(address, 'address_line_1', 'Address', validation_error_builder) \
            .is_required()

        if country == "United Kingdom":
            FieldValidator(postcode, 'postcode', 'Postcode', validation_error_builder) \
                .is_required().is_postcode()

        return validation_error_builder.get()
