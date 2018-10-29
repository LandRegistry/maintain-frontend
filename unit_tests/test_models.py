from maintain_frontend import models
import unittest
from datetime import date


test_llc_item_obj = models.LocalLandChargeItem(
    originating_authority_charge_identifier="an identifier",
    local_land_charge=123,
    registration_date=date(2011, 1, 1),
    charge_type="a charge type",
    charge_geographic_description="a description",
    charge_creation_date=date(2011, 1, 1),
    instrument="An instrument",
    statutory_provision="a provision",
    further_information_location='a location',
    further_information_reference='a reference',
    land_works_particulars="particulars",
    land_capacity_description="a description",
    land_compensation_paid="compensation",
    unique_property_reference_numbers=[123, 456],
    old_register_part="1a",
    originating_authority="an authority",
    migrating_authority="another authority",
    migration_supplier="a supplier",
    expiry_date=date(2011, 1, 1),
    amount_originally_secured="an amount",
    rate_of_interest="a rate",
    end_date=date(2011, 1, 1),
    start_date=date(2011, 1, 1))

test_llc_item_json = {'amount-originally-secured': 'an amount',
                      'charge-creation-date': '2011-01-01',
                      'charge-geographic-description': 'a description',
                      'charge-type': 'a charge type',
                      'end-date': '2011-01-01',
                      'expiry-date': '2011-01-01',
                      'further-information-location': 'a location',
                      'further-information-reference': 'a reference',
                      'instrument': 'An instrument',
                      'land-capacity-description': 'a description',
                      'land-compensation-paid': 'compensation',
                      'land-works-particulars': 'particulars',
                      'local-land-charge': 123,
                      'migrating-authority': 'another authority',
                      'migration-supplier': 'a supplier',
                      'old-register-part': '1a',
                      'originating-authority': 'an authority',
                      'rate-of-interest': 'a rate',
                      'registration-date': '2011-01-01',
                      'start-date': '2011-01-01',
                      'statutory-provision': 'a provision',
                      'originating-authority-charge-identifier': 'an identifier',
                      'unique-property-reference-numbers': [123, 456]}

test_llc_item_json_no_instrument = {'amount-originally-secured': 'an amount',
                                    'charge-geographic-description': 'a description',
                                    'charge-type': 'a charge type',
                                    'end-date': '2011-01-01',
                                    'further-information-location': 'a location',
                                    'further-information-reference': 'a reference',
                                    'instrument': '',
                                    'land-capacity-description': 'a description',
                                    'land-compensation-paid': 'compensation',
                                    'land-works-particulars': 'particulars',
                                    'local-land-charge': 123,
                                    'migrating-authority': 'another authority',
                                    'migration-supplier': 'a supplier',
                                    'old-register-part': '1a',
                                    'originating-authority': 'an authority',
                                    'rate-of-interest': 'a rate',
                                    'registration-date': '2011-01-01',
                                    'start-date': '2011-01-01',
                                    'statutory-provision': 'a provision',
                                    'originating-authority-charge-identifier': 'an identifier',
                                    'unique-property-reference-numbers': [123, 456]}


class TestLocalLandChargeItemModel(unittest.TestCase):

    def test_local_land_charge_item_serialise(self):
        self.assertEqual(test_llc_item_obj.to_json(), test_llc_item_json)

    def test_local_land_charge_item_deserialise(self):
        llc = models.LocalLandChargeItem.from_json(test_llc_item_json)
        self.assertEqual(llc, test_llc_item_obj)
        self.assertIsNone(llc.geometry)

    def test_format_field_for_display_displays_correct_information(self):
        llc = models.LocalLandChargeItem.from_json(test_llc_item_json)
        result = llc.format_field_for_display('instrument')
        self.assertEqual(result, "An instrument")

    def test_format_field_for_display_displays_not_provided(self):
        llc = models.LocalLandChargeItem.from_json(test_llc_item_json_no_instrument)
        result = llc.format_field_for_display('instrument')
        self.assertEqual(result, "Not provided")

    def test_format_date_for_display_displays_does_not_expire(self):
        llc = models.LocalLandChargeItem.from_json(test_llc_item_json_no_instrument)
        result = llc.format_date_for_display('expiry_date')
        self.assertEqual(result, "Does not expire")

    def test_format_date_for_display_displays_not_provided(self):
        llc = models.LocalLandChargeItem.from_json(test_llc_item_json_no_instrument)
        result = llc.format_date_for_display('charge_creation_date')
        self.assertEqual(result, "Not provided")
