from unittest.mock import Mock
from unittest import TestCase
import mock
import json

from maintain_frontend.services.search_by_area import SearchByArea


class TestSearchByArea(TestCase):
    SEARCH_BY_AREA_PATH = 'maintain_frontend.services.search_by_area'

    @mock.patch("{}.LocalLandChargeService".format(SEARCH_BY_AREA_PATH))
    def test_search_by_area_with_bbox_no_paging(
            self,
            mock_local_land_charge_service
    ):
        expected_response = 'some response'

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_response

        mock_local_land_charge_service.return_value.get.return_value = mock_response

        bounding_box = [
            [290000, 910000],
            [290100, 910000],
            [290100, 910100],
            [290000, 910100],
            [290000, 910000]
        ]

        bounding_box_param = json.dumps(bounding_box)

        expected = {
            "type": "Polygon",
            "coordinates": bounding_box,
            "crs": {
                "type": "name",
                "properties": {
                    "name": "EPSG:27700"
                }
            }
        }

        config = {'SEARCH_API_URL': 'TEST'}
        search_by_area = SearchByArea(Mock(), config)
        response = search_by_area.process(bounding_box_param)

        self.assertEqual(response['data'], expected_response)
        mock_local_land_charge_service.return_value.get.assert_called_with(json.dumps(expected))
