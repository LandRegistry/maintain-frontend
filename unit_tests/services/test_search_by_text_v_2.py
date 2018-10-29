from unittest.mock import Mock
from unittest import TestCase
import mock

from maintain_frontend.dependencies.search_api.search_type import SearchType
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.services.search_by_text import SearchByText


class TestSearchByTextV2(TestCase):
    SEARCH_BY_TEXT_PATH = 'maintain_frontend.services.search_by_text'

    def setUp(self):
        self.search_by_text = SearchByText(Mock())

    @mock.patch("{}.AddressesService".format(SEARCH_BY_TEXT_PATH))
    def test_search_by_text_no_search_query(
            self,
            mock_addresses_service
    ):
        response = self.search_by_text.process(None, None, "v2.0")

        self.assertEqual(response['search_message'], "Enter a postcode or location")
        self.assertEqual(response['status'], "error")

        return None

    @mock.patch("{}.AddressesService".format(SEARCH_BY_TEXT_PATH))
    def test_search_by_text_valid_postcode(
        self,
        mock_addresses_service
    ):
        query_string = 'BT1 1AA'

        expected_address_json = [
            {
                'geometry':
                    {'type': 'some type'}
            }
        ]

        self.setup_successful_search_test(
            expected_address_json,
            mock_addresses_service)

        response = self.search_by_text.process(query_string, None, "v2.0")

        self.assertEqual(response['status'], 'success')
        self.assertEqual(response['data'], expected_address_json)
        mock_addresses_service.return_value.get_by.assert_called_with(SearchType.POSTCODE.value, query_string)

    @mock.patch("{}.AddressesService".format(SEARCH_BY_TEXT_PATH))
    def test_search_by_text_invalid_charge_number_prefix(
            self,
            mock_addresses_service
    ):
        query_string = 'llc-1'

        self.setup_successful_search_test(
            [],
            mock_addresses_service
        )

        response = self.search_by_text.process(query_string, None, "v2.0")

        self.assertEqual(response['status'], 'error')
        self.assertEqual(response['search_message'], 'Invalid search, please try again')

    @mock.patch("{}.AddressesService".format(SEARCH_BY_TEXT_PATH))
    def test_search_by_text_invalid_search(
            self,
            mock_addresses_service,
    ):
        query_string = 'random search term'

        mock_addresses_service.return_value.get_by = Mock()
        get_by_address_mock = mock_addresses_service.return_value.get_by
        get_by_address_mock.return_value.status_code = 500

        with self.assertRaises(ApplicationError) as context:
            self.search_by_text.process(query_string, None, "v2.0")

        self.assertEqual(context.exception.http_code, 500)

    @mock.patch("{}.AddressesService".format(SEARCH_BY_TEXT_PATH))
    def test_search_by_text_response_404(
            self,
            mock_addresses_service,
    ):
        query_string = 'random search term'

        mock_addresses_service.return_value.get_by = Mock()
        get_by_address_mock = mock_addresses_service.return_value.get_by
        get_by_address_mock.return_value.status_code = 404

        response = self.search_by_text.process(query_string, None, "v2.0")

        self.assertEqual(response['search_message'], "Enter a valid postcode or location")
        self.assertEqual(response['status'], "error")

    @staticmethod
    def setup_successful_search_test(
            expected_response,
            mock_address_service
    ):
        mock_address_service.return_value.get_by = Mock()

        get_by_address_mock = mock_address_service.return_value.get_by
        get_by_address_mock.return_value.status_code = 200
        get_by_address_mock.return_value.json.return_value = expected_response
