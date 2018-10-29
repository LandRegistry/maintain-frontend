from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from unittest.mock import patch
from flask import url_for
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LightObstructionNoticeItem
from maintain_frontend.constants.permissions import Permissions
from unit_tests.mock_data.mock_land_charges import get_mock_lon_item


class TestModifyLONDetails(TestCase):

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    @patch('maintain_frontend.view_modify_lon.modify_lon_details.LocalLandChargeService')
    def test_modify_lon_details_get_with_no_state(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]
        self.mock_session.return_value.add_lon_charge_state = None

        response = self.client.get(url_for('modify_lon.modify_lon_details_get', charge_id=123))

        self.assert_status(response, 302)

    @patch('maintain_frontend.view_modify_lon.modify_lon_details.calc_display_id')
    @patch('maintain_frontend.view_modify_lon.modify_lon_details.LocalLandChargeService')
    def test_modify_lon_details_get_with_state(self, mock_service, mock_calc_display_id):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]
        self.mock_session.return_value.add_lon_charge_state = LightObstructionNoticeItem.from_json(get_mock_lon_item())
        mock_calc_display_id.return_value = "LLC-TST"

        response = self.client.get(url_for('modify_lon.modify_lon_details_get', charge_id='LLC-TST'))

        self.assert_status(response, 200)
        self.assert_template_used('modify_lon_details.html')

    @patch('maintain_frontend.view_modify_lon.modify_lon_details.LocalLandChargeService')
    def test_modify_lon_details_cancel_changes(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]
        self.mock_session.return_value.add_lon_charge_state = LightObstructionNoticeItem()
        self.mock_session.return_value.edited_fields = {"test-change": "test-change"}

        response = self.client.get(url_for('modify_lon.clear_lon_changes', charge_id='LLC-TST'))

        self.assert_status(response, 302)
        self.assertEqual(self.mock_session.return_value.edited_fields, {})
        self.assertIsNone(self.mock_session.return_value.add_lon_charge_state)

    @patch('maintain_frontend.view_modify_lon.modify_lon_details.MaintainApiService')
    @patch('maintain_frontend.view_modify_lon.modify_lon_details.AuditAPIService')
    def test_modify_land_charge_confirm(self, mock_audit, mock_maintain_api_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        lon = LightObstructionNoticeItem()
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]
        self.mock_session.return_value.add_lon_charge_state = lon
        self.mock_session.return_value.edited_fields = {"test-change": "test-change"}

        response = self.client.post(url_for('modify_lon.modify_land_charge_confirm', charge_id='LLC-TST'))

        self.assert_status(response, 302)
        self.assertIsNone(self.mock_session.return_value.edited_fields)
        self.assertIsNone(self.mock_session.return_value.add_lon_charge_state)
        mock_audit.audit_event.assert_called_with("Vary request submitted", supporting_info={'id': 'LLC-TST'})
        mock_maintain_api_service.update_charge.assert_called_with(lon)
