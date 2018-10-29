from unittest.mock import Mock, patch
from unittest import TestCase
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.services.search_by_postcode import SearchByPostcode


class TestSearchByPostcode(TestCase):
    SEARCH_BY_POSTCODE_PATH = 'maintain_frontend.services.search_by_postcode'

    def setUp(self):
        self.search_by_postcode = SearchByPostcode(Mock())

    @patch("{}.AddressesService".format(SEARCH_BY_POSTCODE_PATH))
    def test_search_by_postcode_no_search_query(self, mock_addresses_service):
        response = self.search_by_postcode.process(None, None)

        self.assertEqual(response['search_message'], "Enter a postcode")
        self.assertEqual(response['inline_message'],
                         "Search for a different postcode if the address you need is not listed.")
        self.assertEqual(response['status'], "error")
        mock_addresses_service.assert_not_called()

    @patch("{}.AddressesService".format(SEARCH_BY_POSTCODE_PATH))
    def test_search_by_postcode_invalid_query(self, mock_addresses_service):
        response = self.search_by_postcode.process('ABC', None)

        self.assertEqual(response['search_message'], "No match found")
        self.assertEqual(response['inline_message'], "Try a different postcode")
        self.assertEqual(response['status'], "error")
        mock_addresses_service.get_by.assert_not_called()

    @patch("{}.AddressesService".format(SEARCH_BY_POSTCODE_PATH))
    def test_search_by_postcode_valid(self, mock_addresses_service):
        response = Mock()
        response.status_code = 200
        response.json.return_value = "abc"

        mock_addresses_service.return_value.get_by.return_value = response
        response = self.search_by_postcode.process('AB1 2CD', None)

        self.assertEqual(response['status'], "success")
        self.assertEqual(response['data'], "abc")

        mock_addresses_service.get_by.assert_called()

    @patch("{}.AddressesService".format(SEARCH_BY_POSTCODE_PATH))
    def test_search_by_postcode_valid_400_response(self, mock_addresses_service):
        response = Mock()
        response.status_code = 400

        mock_addresses_service.return_value.get_by.return_value = response
        response = self.search_by_postcode.process('AB1 2CD', None)

        self.assertEqual(response['status'], "error")
        self.assertEqual(response['search_message'], "No match found")
        self.assertEqual(response['inline_message'], "Try a different postcode")

        mock_addresses_service.get_by.assert_called()

    @patch("{}.AddressesService".format(SEARCH_BY_POSTCODE_PATH))
    def test_search_by_postcode_valid_404_response(self, mock_addresses_service):
        response = Mock()
        response.status_code = 404

        mock_addresses_service.return_value.get_by.return_value = response
        response = self.search_by_postcode.process('AB1 2CD', None)

        self.assertEqual(response['status'], "error")
        self.assertEqual(response['search_message'], "No match found")
        self.assertEqual(response['inline_message'], "Try a different postcode")

        mock_addresses_service.get_by.assert_called()

    @patch("{}.AddressesService".format(SEARCH_BY_POSTCODE_PATH))
    def test_search_by_postcode_valid_500_response(self, mock_addresses_service):
        response = Mock()
        response.status_code = 500

        mock_addresses_service.return_value.get_by.return_value = response

        self.assertRaises(ApplicationError, self.search_by_postcode.process, 'AB1 2CD', None)
        mock_addresses_service.get_by.assert_called()
