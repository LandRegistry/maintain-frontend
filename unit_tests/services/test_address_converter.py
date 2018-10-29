from unittest import TestCase
from maintain_frontend.services.address_converter import AddressConverter


class TestAddressConverter(TestCase):

    def test_address_standard(self):

        address = {
            'address_line_1': '28 test st',
            'address_line_2': 'flat 6',
            'address_line_3': 'town',
            'address_line_4': 'county',
            'address_line_5': '',
            'address_line_6': '',
            'postcode': 'postcode',
            'country': 'United Kingdom'
        }

        loaded_address = AddressConverter.condense_address(address)

        expected = {
            'line-1': '28 test st',
            'line-2': 'flat 6',
            'line-3': 'town',
            'line-4': 'county',
            'postcode': 'POSTCODE',
            'country': 'United Kingdom'
        }

        self.assertDictEqual(loaded_address, expected)

    def test_address_missing_lines(self):

        address = {
            'address_line_1': '',
            'address_line_2': '28 test st',
            'address_line_3': 'flat 6',
            'address_line_4': '',
            'address_line_5': 'town',
            'address_line_6': 'county',
            'postcode': 'postcode',
            'country': 'United Kingdom'
        }

        loaded_address = AddressConverter.condense_address(address)

        expected = {
            'line-1': '28 test st',
            'line-2': 'flat 6',
            'line-3': 'town',
            'line-4': 'county',
            'postcode': 'POSTCODE',
            'country': 'United Kingdom'
        }

        self.assertDictEqual(loaded_address, expected)

    def test_to_charge_address(self):

        address = {
            'line_1': '28 test st',
            'line_2': 'flat 6',
            'line_3': 'line 3',
            'line_4': 'line 4',
            'line_5': 'line 5',
            'line_6': '',
            'postcode': 'EX4 7AN',
            'uprn': 1233454565767,
            'geometry': {
                "coordinates": [
                    293277,
                    93555
                ],
                "crs": {
                    "properties": {
                        "name": "urn:ogc:def:crs:EPSG::27700"
                    },
                    "type": "name"
                },
                "type": "Point"
            }
        }

        address = AddressConverter.to_charge_address(address)

        expected = {
            'line-1': '28 test st',
            'line-2': 'flat 6',
            'line-3': 'line 3',
            'line-4': 'line 4',
            'line-5': 'line 5',
            'line-6': '',
            'postcode': 'EX4 7AN',
            'unique-property-reference-number': 1233454565767
        }

        self.assertDictEqual(address, expected)
