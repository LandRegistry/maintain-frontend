from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from unittest.mock import patch, MagicMock
from flask import url_for
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.constants.permissions import Permissions
from unit_tests.mock_data.mock_land_charges import get_mock_lon_item


class TestViewLONCharge(TestCase):

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    @patch('maintain_frontend.view_modify_lon.view_lon.AuditAPIService')
    @patch('maintain_frontend.view_modify_lon.view_lon.LocalLandChargeService')
    def test_view_invalid_id(self, mock_service, mock_audit):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.retrieve_llc]

        response = self.client.get(url_for('view_lon.view_lon', charge_id=123))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/page-not-found')

    @patch('maintain_frontend.view_modify_lon.view_lon.StorageAPIService')
    @patch('maintain_frontend.view_modify_lon.view_lon.AuditAPIService')
    @patch('maintain_frontend.view_modify_lon.view_lon.LocalLandChargeService')
    def test_view_found(self, mock_service, mock_audit, mock_storage):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.retrieve_llc]

        mock_response = MagicMock()
        mock_service.return_value.get_by_charge_number.return_value = mock_response
        mock_response.status_code = 200
        mock_response.json.return_value = [{"item": get_mock_lon_item(), "display_id": "LLC-TST", "cancelled": False}]
        response = self.client.get(url_for('view_lon.view_lon', charge_id='LLC-TST'))

        self.assert_status(response, 200)

    @patch('maintain_frontend.view_modify_lon.view_lon.AuditAPIService')
    @patch('maintain_frontend.view_modify_lon.view_lon.LocalLandChargeService')
    def test_view_not_found(self, mock_service, mock_audit):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.retrieve_llc]

        mock_response = MagicMock()
        mock_service.return_value.get_by_charge_number.return_value = mock_response
        mock_response.status_code = 404
        response = self.client.get(url_for('view_lon.view_lon', charge_id='LLC-TST'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/page-not-found')
