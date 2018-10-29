from unittest import TestCase

from maintain_frontend.add_land_charge.validation.address_for_charge_validator import AddressForChargeValidator

VALID_ADDRESS = {'line-1': '1 test street'}
VALID_DESCRIPTION = "This is a valid description"
TOO_LONG_DESCRIPTION = "a" * 1001


class TestAddressForChargeValidator(TestCase):

    def test_address_required_for_address_radio_button_no_address(self):
        result = AddressForChargeValidator.validate('ProvideAddress', None, VALID_DESCRIPTION).errors

        self.assertEqual(len(result), 1)
        self.assertEqual(result['search_term'].summary_message, 'Enter a postcode')
        self.assertEqual(result['search_term'].inline_message,
                         'Search for a different postcode if the address you need is not listed.')

    def test_address_required_for_address_radio_button(self):
        result = AddressForChargeValidator.validate('Address', VALID_ADDRESS, VALID_DESCRIPTION).errors
        self.assertEqual(len(result), 0)

    def test_description_required_for_no_radio_button_no_description(self):
        result = AddressForChargeValidator.validate('No', VALID_ADDRESS, None).errors

        self.assertEqual(len(result), 1)
        self.assertEqual(result['charge-geographic-description'].summary_message, 'Describe the charge location')
        self.assertEqual(result['charge-geographic-description'].inline_message,
                         'Explain how to find the charge without an address. '
                         'For example, use a nearby landmark as a reference point. ')

    def test_description_required_for_no_radio_button_too_long_description(self):
        result = AddressForChargeValidator.validate('No', VALID_ADDRESS, TOO_LONG_DESCRIPTION).errors

        self.assertEqual(len(result), 1)
        self.assertEqual(result['charge-geographic-description'].summary_message, 'Answer is too long')
        self.assertEqual(result['charge-geographic-description'].inline_message,
                         'Reduce your answer to 1000 characters or less')

    def test_description_required_for_no_radio_button(self):
        result = AddressForChargeValidator.validate('ProvideAddress', VALID_ADDRESS, VALID_DESCRIPTION).errors
        self.assertEqual(len(result), 0)

    def test_no_radio_button_selected(self):
        result = AddressForChargeValidator.validate(None, VALID_ADDRESS, VALID_DESCRIPTION).errors

        self.assertEqual(len(result), 1)
        self.assertEqual(result['address-from-group'].summary_message, 'Choose One')
