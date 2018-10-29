from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class AddressForChargeValidator(object):

    @staticmethod
    def validate(has_address, address, charge_geographic_description):
        validation_error_builder = ValidationErrorBuilder()

        if has_address == 'ProvideAddress':
            FieldValidator(address, 'search_term', 'Charge Address', validation_error_builder,
                           summary_message='Enter a postcode',
                           inline_message='Search for a different postcode if the address you need is not listed.') \
                .is_required()

        elif has_address == 'No':
            FieldValidator(charge_geographic_description, 'charge-geographic-description',
                           'Charge Geographic Description', validation_error_builder,
                           summary_message='Describe the charge location',
                           inline_message='Explain how to find the charge without an address. '
                                          'For example, use a nearby landmark as a reference point. ') \
                .is_required()

            FieldValidator(charge_geographic_description, 'charge-geographic-description',
                           'Charge Geographic Description', validation_error_builder,
                           summary_message='Answer is too long',
                           inline_message='Reduce your answer to 1000 characters or less')\
                .is_length_less_than_or_equal_to(1000)

        else:
            FieldValidator(has_address, 'address-from-group', 'Choose One', validation_error_builder,
                           summary_message='Choose One') \
                .is_required()

        return validation_error_builder.get()
