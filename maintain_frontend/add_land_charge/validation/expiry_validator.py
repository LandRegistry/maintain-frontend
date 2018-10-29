from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.fieldset_validator import FieldsetValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class ExpiryValidator(object):
    @staticmethod
    def validate(does_charge_expire, charge_expiry_day, charge_expiry_month, charge_expiry_year):
        """Specifies which validation methods should be called for each input FieldValidator.


        parameters:
            - does_charge_expire: Whether or not the charge expires.
            - charge_expiry_day: The day that the charge expires.
            - charge_expiry_month: The month that the charge expires.
            - charge_expiry_year: The year that the charge expires.

        returns:
            dict: An instance of ValidationErrorBuilder with a ValidationError dict and a heading summary message.
        """

        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(does_charge_expire, 'does_charge_expire', None, validation_error_builder,
                       summary_message='Choose one option',
                       inline_message='Choose \'No\' if you don’t have this information.') \
            .is_required()

        if does_charge_expire == 'yes':
            charge_expiry_date = [charge_expiry_day, charge_expiry_month, charge_expiry_year]

            # TODO(refactor): Refactor this class to handle this case more gracefully.
            if not (charge_expiry_day or charge_expiry_month or charge_expiry_year):
                validation_error_builder.add_error(
                    FieldsetValidator(None, 'charge_expiry_date', None, validation_error_builder),
                    'Enter an expiry date'
                )

            FieldValidator(charge_expiry_year, "charge_expiry_date", 'Date', validation_error_builder,
                           summary_message="Date is invalid", inline_message="Year must be in the format YYYY") \
                .is_year_format()

            FieldsetValidator(charge_expiry_date, 'charge_expiry_date',
                              'Date', validation_error_builder) \
                .is_valid_date()

        return validation_error_builder.get()
