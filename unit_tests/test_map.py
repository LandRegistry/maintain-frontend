from unittest import TestCase
from maintain_frontend.main import app
from unit_tests.utilities import Utilities
from unittest.mock import patch
from requests.models import Response
import json


class TestMap(TestCase):

    def setUp(self):
        self.app = app.test_client()
        Utilities.mock_session_cookie_unittest(self)

    @patch('maintain_frontend.map.map.LocalAuthorityService')
    def test_local_authority_service_boundingbox_success(self, mock_la_api):
        local_authority_name = "Winchester District (B)"
        mock_response = Response()
        mock_response.status_code = 200
        mock_content = {
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[438199.90401036787, 106603.8042336921],
                                 [438199.90401036787, 144431.39619812733],
                                 [468030.1970266425, 144431.39619812733],
                                 [468030.1970266425, 106603.8042336921],
                                 [438199.90401036787, 106603.8042336921]]]},
            "type": "Feature",
            "properties": {"local-authority-name": local_authority_name}
        }

        mock_response._content = json.dumps(mock_content).encode()

        mock_la_api.return_value.get_bounding_box.return_value = mock_response

        response = self.app.get("/_authorities/{}/boundingbox".format(local_authority_name),
                                headers=[('X-Requested-With', 'XMLHttpRequest')])
        self.assertEqual(response.status_code, 200)
        response_object = json.loads(response.data.decode())
        self.assertEqual(response_object, mock_content)

    @patch('maintain_frontend.map.map.LocalAuthorityService')
    def test_local_authority_service_boundingbox_fail_not_xhr(self, mock_la_api):
        local_authority_name = "Winchester District (B)"

        response = self.app.get("/_authorities/{}/boundingbox".format(local_authority_name))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'http://localhost/error')
