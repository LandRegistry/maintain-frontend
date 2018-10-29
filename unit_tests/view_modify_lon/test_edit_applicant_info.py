from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from flask import url_for
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.models import LightObstructionNoticeItem
from unit_tests.mock_data.mock_land_charges import get_mock_lon_item
from unittest.mock import patch


class TestEditApplicantInfo(TestCase):
    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_edit_applicant_info_get_with_state(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]
        mock_lon = LightObstructionNoticeItem.from_json(get_mock_lon_item())
        self.mock_session.return_value.add_lon_charge_state = mock_lon

        response = self.client.get(url_for('modify_lon.edit_applicant_info_get'))

        self.assert_status(response, 200)
        self.assert_template_used('applicant_info.html')

    def test_edit_applicant_name_info_get(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]

        mock_lon = LightObstructionNoticeItem()
        self.mock_session.return_value.add_lon_charge_state = mock_lon
        self.mock_session.add_lon_charge_state.applicant_name = None

        response = self.client.get(url_for('modify_lon.edit_applicant_info_get'))

        self.assert_status(response, 200)
        self.assert_template_used('applicant_info.html')

    def test_edit_applicant_address_info_get(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]

        mock_lon = LightObstructionNoticeItem()
        self.mock_session.return_value.add_lon_charge_state = mock_lon
        self.mock_session.add_lon_charge_state.applicant_address = None

        response = self.client.get(url_for('modify_lon.edit_applicant_info_get'))

        self.assert_status(response, 200)
        self.assert_template_used('applicant_info.html')

    def test_edit_applicant_info_get_with_no_state(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]
        self.mock_session.return_value.add_lon_charge_state = None

        response = self.client.get(url_for('modify_lon.edit_applicant_info_get'))

        self.assert_status(response, 302)

    @patch('maintain_frontend.view_modify_lon.edit_applicant_info.request')
    @patch('maintain_frontend.view_modify_lon.edit_applicant_info.AddressConverter')
    @patch('maintain_frontend.view_modify_lon.edit_applicant_info.ApplicantInfoValidator')
    def test_edit_applicant_info_update_success(self, mock_validator, mock_converter, mock_request):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]

        mock_lon = LightObstructionNoticeItem.from_json(get_mock_lon_item())
        mock_edited_name = "Test"
        mock_edited_address = {
            "line-1": "street",
            "line-2": "town",
            "postcode": "postcode",
            "country": "country"
        }

        self.mock_session.return_value.add_lon_charge_state = mock_lon
        self.mock_session.return_value.edited_fields = {}

        mock_validator.validate.return_value.errors = None
        mock_request.form.get.return_value = mock_edited_name
        mock_converter.condense_address.return_value = mock_edited_address

        response = self.client.post(url_for('modify_lon.edit_applicant_info_post'))

        self.assert_status(response, 302)
        self.assertEqual(self.mock_session.return_value.add_lon_charge_state.applicant_name, mock_edited_name)
        self.assertEqual(self.mock_session.return_value.add_lon_charge_state.applicant_address, mock_edited_address)
        self.assertEqual(self.mock_session.return_value.edited_fields['applicant-name'], "Name")
        self.assertEqual(self.mock_session.return_value.edited_fields['applicant-address'], "Address")

    @patch('maintain_frontend.view_modify_lon.edit_applicant_info.ApplicantInfoValidator')
    def test_edit_applicant_info_update_errors(self, mock_validator):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]

        self.mock_session.return_value.add_lon_charge_state = LightObstructionNoticeItem()
        mock_validator.validate.return_value.errors = {"error": "test-error"}

        response = self.client.post(url_for('modify_lon.edit_applicant_info_post'))

        self.assert_status(response, 400)
        self.assert_template_used('applicant_info.html')
        self.assert_context("validation_errors", {"error": "test-error"})
