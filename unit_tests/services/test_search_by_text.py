from unittest.mock import Mock
from unittest import TestCase
import mock

from maintain_frontend.dependencies.search_api.search_type import SearchType
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.services.search_by_text import SearchByText


class TestSearchByText(TestCase):
    SEARCH_BY_TEXT_PATH = 'maintain_frontend.services.search_by_text'

    def setUp(self):
        self.search_by_text = SearchByText(Mock())

    @mock.patch("{}.AddressesService".format(SEARCH_BY_TEXT_PATH))
    def test_search_by_text_no_search_query(
            self,
            mock_addresses_service
    ):
        response = self.search_by_text.process(None, None)

        self.assertEqual(response['search_message'], "Enter a postcode or location")
        self.assertEqual(response['status'], "error")

        return None

    @mock.patch("{}.SearchByText.get_all_coordinates".format(SEARCH_BY_TEXT_PATH))
    @mock.patch("{}.AddressesService".format(SEARCH_BY_TEXT_PATH))
    def test_search_by_text_valid_postcode(
        self,
        mock_addresses_service,
        mock_get_all_coordinates
    ):
        query_string = 'BT1 1AA'
        expected_coords = [
            [1, 1],
            [2, 2],
            [3, 3],
            [4, 4]
        ]

        expected_address_json = [
            {
                'geometry':
                    {'type': 'some type'}
            }
        ]

        self.setup_successful_search_test(
            expected_coords,
            expected_address_json,
            mock_addresses_service,
            mock_get_all_coordinates)

        response = self.search_by_text.process(query_string, None)

        self.assertEqual(response['coordinates'], expected_coords)
        self.assertEqual(response['status'], 'success')
        self.assertEqual(response['type'], expected_address_json[0]['geometry']['type'])
        mock_addresses_service.return_value.get_by.assert_called_with(SearchType.POSTCODE.value, query_string)

    @mock.patch("{}.SearchByText.get_all_coordinates".format(SEARCH_BY_TEXT_PATH))
    @mock.patch("{}.AddressesService".format(SEARCH_BY_TEXT_PATH))
    def test_search_by_text_valid_charge_number_prefix(
            self,
            mock_addresses_service,
            mock_get_all_coordinates
    ):
        query_string = 'llc-1'

        self.setup_successful_search_test(
            [],
            [],
            mock_addresses_service,
            mock_get_all_coordinates
        )

        response = self.search_by_text.process(query_string, None)

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
            self.search_by_text.process(query_string, None)

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

        response = self.search_by_text.process(query_string, None)

        self.assertEqual(response['search_message'], "Enter a valid postcode or location")
        self.assertEqual(response['status'], "error")

    @mock.patch("{}.url_for".format(SEARCH_BY_TEXT_PATH))
    @mock.patch("{}.AddressesService".format(SEARCH_BY_TEXT_PATH))
    def test_get_all_coordinates_polygon(
            self,
            mock_addresses_service,
            mock_url_for
    ):
        expected_coords = [
            [1, 2],
            [3, 4],
            [5, 6],
            [7, 8],
            [9, 0]
        ]
        features = [
            {"type": "Feature",
             "geometry": {
                 "type": "Polygon",
                 "coordinates": [
                     expected_coords
                 ]},
             "properties": {"id": 1}
             }
        ]

        mock_url_for.return_value = 'http://www.google.com'

        response = self.search_by_text.get_all_coordinates(features)

        self.assertEqual(features[0]['geometry']['coordinates'][0], response)

    @mock.patch("{}.url_for".format(SEARCH_BY_TEXT_PATH))
    @mock.patch("{}.AddressesService".format(SEARCH_BY_TEXT_PATH))
    def test_get_all_coordinates_linestring(
            self,
            mock_addresses_service,
            mock_url_for
    ):
        expected_coords = [1, 2]

        feature = [
            {"type": "Feature",
             "geometry": {
                 "type": "LineString",
                 "coordinates": expected_coords
             },
             "properties": {"id": 1}
             }
        ]

        mock_url_for.return_value = 'http://www.google.com'

        response = self.search_by_text.get_all_coordinates(feature)

        self.assertEqual(feature[0]['geometry']['coordinates'], response)

    @mock.patch("{}.url_for".format(SEARCH_BY_TEXT_PATH))
    @mock.patch("{}.AddressesService".format(SEARCH_BY_TEXT_PATH))
    def test_get_all_coordinates_point(
            self,
            mock_addresses_service,
            mock_url_for
    ):
        expected_coords = [1, 2]

        feature = [
            {"type": "Feature",
             "geometry": {
                 "type": "Point",
                 "coordinates": expected_coords
             },
             "properties": {"id": 1}
             }
        ]

        mock_url_for.return_value = 'http://www.google.com'

        response = self.search_by_text.get_all_coordinates(feature)

        self.assertEqual(expected_coords, response[0])

    @mock.patch("{}.url_for".format(SEARCH_BY_TEXT_PATH))
    @mock.patch("{}.AddressesService".format(SEARCH_BY_TEXT_PATH))
    def test_get_all_coordinates_featurecollection(
            self,
            mock_addresses_service,
            mock_url_for
    ):
        mock_response = [{"geometry": {"type": "FeatureCollection", "features": []}, "display_id": "LLC-1"}]

        feature = {"type": "Feature",
                   "geometry": {
                       "type": "Polygon",
                       "coordinates": [
                           [[1, 2],
                            [3, 4],
                            [5, 6],
                            [7, 8],
                            [9, 0]]
                       ]},
                   "properties": {"id": 1}
                   }

        for _ in range(0, 2):
            mock_response[0]['geometry']['features'].append(feature)

        mock_url_for.return_value = 'http://www.google.com'

        response = self.search_by_text.get_all_coordinates(mock_response)

        self.assertEqual(feature['geometry']['coordinates'][0] + feature['geometry']['coordinates'][0],
                         response)

    @mock.patch("{}.url_for".format(SEARCH_BY_TEXT_PATH))
    @mock.patch("{}.AddressesService".format(SEARCH_BY_TEXT_PATH))
    def test_get_all_coordinates_feature(
            self,
            mock_addresses_service,
            mock_url_for
    ):
        mock_response = [{"geometry": {"type": "FeatureCollection", "features": []}, "display_id": "LLC-1"}]

        feature = {"type": "Feature",
                   "geometry": {
                       "type": "Point",
                       "coordinates": [
                           [[1, 2],
                            [3, 4],
                            [5, 6],
                            [7, 8],
                            [9, 0]]
                       ]
                   },
                   "properties": {"id": 1}
                   }

        mock_response[0]['geometry']['features'].append(feature)
        mock_url_for.return_value = 'http://www.google.com'

        response = self.search_by_text.get_all_coordinates(mock_response)

        self.assertEqual([feature['geometry']['coordinates']], response)

    @staticmethod
    def setup_successful_search_test(
            expected_coords,
            expected_response,
            mock_address_service,
            mock_get_all_coordinates
    ):
        mock_address_service.return_value.get_by = Mock()

        get_by_address_mock = mock_address_service.return_value.get_by
        get_by_address_mock.return_value.status_code = 200
        get_by_address_mock.return_value.json.return_value = expected_response

        if mock_get_all_coordinates is not None:
            mock_get_all_coordinates.return_value = expected_coords
