from unittest import TestCase
from maintain_frontend import main
from unit_tests.utilities import Utilities
from unittest.mock import patch, MagicMock
from flask import g
from maintain_frontend.dependencies.search_api.local_land_charge_service import LocalLandChargeService

BASE64_BOUNDING_BOX = "eyJjb29yZGluYXRlcyI6WzQ0ODY4MS41Mzc1MDAwMDAwMywyNzk2NTkuMTEyNV0sInR5cGUiOiJQb2ludCJ9"


class TestLocalLandChargeApiService(TestCase):
    def setUp(self):
        self.app = main.app.test_client()
        Utilities.mock_session_cookie_unittest(self)

    @patch('maintain_frontend.dependencies.search_api.local_land_charge_service.current_app')
    def test_get_with_bounding_box(self, mock_current_app):
        with main.app.test_request_context():
            g.requests = MagicMock()
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = {'results': [{"abc": "def"}]}

            g.requests.post.return_value = response
            search_api = 'abc'
            mock_current_app.config = {'SEARCH_API_URL': search_api}

            local_land_charge_service = LocalLandChargeService(mock_current_app.config)

            response = local_land_charge_service.get(BASE64_BOUNDING_BOX)

            self.assertEqual(response.status_code, 200)

            g.requests.post.assert_called_with(
                "http://{}/v2.0/search/local_land_charges".format(search_api),
                data=BASE64_BOUNDING_BOX,
                headers={'Content-Type': 'application/json'}
            )

    @patch('maintain_frontend.dependencies.search_api.local_land_charge_service.current_app')
    def test_get_by_charge_number(self, mock_current_app):
        with main.app.test_request_context():
            g.requests = MagicMock()
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = {'results': [{"abc": "def"}]}

            g.requests.get.return_value = response
            search_api = 'abc'
            mock_current_app.config = {'SEARCH_API_URL': search_api}
            charge_number = 'LLC-1'

            local_land_charge_service = LocalLandChargeService(mock_current_app.config)

            response = local_land_charge_service.get_by_charge_number(charge_number)

            self.assertEqual(response.status_code, 200)

            g.requests.get.assert_called_with(
                "http://{}/v2.0/search/local_land_charges/{}".format(
                    search_api, charge_number),
                params=None
            )

    @patch('maintain_frontend.dependencies.search_api.local_land_charge_service.current_app')
    def test_get_history_for_charge(self, mock_current_app):
        with main.app.test_request_context():
            g.requests = MagicMock()
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = {'results': [{"abc": "def"}]}

            g.requests.get.return_value = response
            search_api = 'abc'
            mock_current_app.config = {'SEARCH_API_URL': search_api}
            charge_number = 'LLC-1'

            local_land_charge_service = LocalLandChargeService(mock_current_app.config)

            response = local_land_charge_service.get_history_for_charge(charge_number)

            self.assertEqual(response.status_code, 200)

            g.requests.get.assert_called_with(
                "http://{}/v2.0/search/local_land_charges/{}/history".format(
                    search_api, charge_number),
                params=None
            )
