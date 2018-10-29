from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from flask import url_for
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.models import LightObstructionNoticeItem
from unit_tests.mock_data.mock_land_charges import get_mock_lon_item
from unittest.mock import patch


class TestEditLonLandInterest(TestCase):
    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_edit_lon_land_interest_get_with_state(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]
        mock_lon = LightObstructionNoticeItem.from_json(get_mock_lon_item())
        self.mock_session.return_value.add_lon_charge_state = mock_lon

        response = self.client.get(url_for('modify_lon.edit_lon_land_interest_get'))

        self.assert_status(response, 200)
        self.assert_template_used('lon_land_interest.html')

    def test_edit_lon_land_interest_get_with_no_state(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]
        self.mock_session.return_value.add_lon_charge_state = None

        response = self.client.get(url_for('modify_lon.edit_lon_land_interest_get'))

        self.assert_status(response, 302)

    @patch('maintain_frontend.view_modify_lon.edit_lon_land_interest.request')
    @patch('maintain_frontend.view_modify_lon.edit_lon_land_interest.ValidationErrorBuilder')
    def test_edit_lon_land_interest_update_success(self, mock_validator, mock_request):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]

        mock_lon = LightObstructionNoticeItem.from_json(get_mock_lon_item())

        self.mock_session.return_value.add_lon_charge_state = mock_lon
        self.mock_session.return_value.edited_fields = {}

        mock_validator.return_value.errors = None
        mock_request.form.get.return_value = "tenant"

        response = self.client.post(url_for('modify_lon.edit_lon_land_interest_post'))

        self.assertEqual(self.mock_session.return_value.add_lon_charge_state.servient_land_interest_description,
                         "tenant")
        self.assertEqual(self.mock_session.return_value.edited_fields['servient-land-interest-description'],
                         "Interest")
        self.assert_status(response, 302)

    @patch('maintain_frontend.view_modify_lon.edit_lon_land_interest.request')
    @patch('maintain_frontend.view_modify_lon.edit_lon_land_interest.ValidationErrorBuilder')
    @patch('maintain_frontend.view_modify_lon.edit_lon_land_interest.render_template')
    def test_edit_lon_land_interest_other_missing_details(self, mock_render_template, mock_validator, mock_request):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]

        mock_lon = LightObstructionNoticeItem.from_json(get_mock_lon_item())
        self.mock_session.return_value.add_lon_charge_state = mock_lon
        self.mock_session.return_value.edited_fields = {}

        mock_request.form.get.side_effect = ["Other", ""]
        mock_validator.return_value.errors = {"error": "test-error"}
        mock_render_template.return_value = "Template was called"

        response = self.client.post(url_for('modify_lon.edit_lon_land_interest_post'))

        self.assert_status(response, 400)
        mock_render_template.assert_called()

    @patch('maintain_frontend.view_modify_lon.edit_lon_land_interest.ValidationErrorBuilder')
    def test_edit_lon_land_interest_update_errors(self, mock_validator):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]

        self.mock_session.return_value.add_lon_charge_state = LightObstructionNoticeItem()
        mock_validator.return_value.errors = {"error": "test-error"}

        response = self.client.post(url_for('modify_lon.edit_lon_land_interest_post'))

        self.assert_status(response, 400)
        self.assert_template_used('lon_land_interest.html')
        self.assert_context("validation_errors", {"error": "test-error"})
