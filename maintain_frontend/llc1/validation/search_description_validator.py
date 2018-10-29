from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class SearchDescriptionValidator(object):

    @staticmethod
    def validate(location_info, has_address):
        validation_error_builder = ValidationErrorBuilder()

        if has_address == 'ProvideAddress':
            FieldValidator(location_info, 'search_term', 'Charge Address', validation_error_builder,
                           summary_message='Choose an address',
                           inline_message='Search for a different postcode if the address you need is not listed.') \
                .is_required()

        elif has_address == 'No':
            FieldValidator(location_info, 'charge-geographic-description',
                           'Charge Geographic Description', validation_error_builder,
                           summary_message='Describe the search area',
                           inline_message='Explain where you want to search without an address. '
                                          'For example, use a nearby landmark as a reference point. ') \
                .is_required()

            FieldValidator(location_info, 'charge-geographic-description',
                           'Charge Geographic Description', validation_error_builder,
                           summary_message='Answer is too long',
                           inline_message='Reduce your answer to 1000 characters or less') \
                .is_length_less_than_or_equal_to(1000)

        else:
            FieldValidator(has_address, 'address-from-group', 'Choose one option',
                           validation_error_builder,
                           summary_message='Choose one option') \
                .is_required()

        validation_errors = validation_error_builder.get()

        return validation_errors
