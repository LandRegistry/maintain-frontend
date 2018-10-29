from maintain_frontend import main
from flask_testing import TestCase as TestCase
from unit_tests.utilities import Utilities
from unittest.mock import patch
from flask import url_for
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.constants.permissions import Permissions

ADD_CHARGE_STATE = LocalLandChargeItem()
ADDITIONAL_INFO_PATH = 'maintain_frontend.view_modify_land_charge.edit_additional_info'
VALID_DATA = {
    'additional-info': 'some info',
    'reference': '',
}


class TestEditAdditionalInfoView(TestCase):
    render_templates = False

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    @patch('{}.AddChargeAdditionalInfoValidator'.format(ADDITIONAL_INFO_PATH))
    def test_additional_info_post_success(self, mock_validator):
        mock_validator.validate.return_value.errors = []
        self.mock_session.return_value.add_charge_state = ADD_CHARGE_STATE
        ADD_CHARGE_STATE.local_land_charge = 1
        self.mock_session.return_value.edited_fields = []

        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        response = self.client.post(url_for('modify_land_charge.post_additional_info'), data=VALID_DATA)
        self.assertTrue('further_information' in self.mock_session.return_value.edited_fields)
        self.assertStatus(response, 302)
        self.assertRedirects(response, url_for('modify_land_charge.modify_land_charge', local_land_charge="LLC-1"))

    @patch('{}.get_source_information_list'.format(ADDITIONAL_INFO_PATH))
    @patch('{}.AddChargeAdditionalInfoValidator'.format(ADDITIONAL_INFO_PATH))
    def test_additional_info_post_validation_error(self, mock_validator, get_source_information_list):
        mock_validator.validate.return_value.errors = [{'field': 'validation error'}]
        self.mock_session.return_value.add_charge_state = ADD_CHARGE_STATE
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        response = self.client.post(url_for('modify_land_charge.post_additional_info'), data={
            'additional-info': '',
            'reference': 'e',
        })

        get_source_information_list.assert_not_called()

        self.assertStatus(response, 400)
        self.assert_template_used('additional_info.html')

    @patch('{}.get_source_information_list'.format(ADDITIONAL_INFO_PATH))
    @patch('{}.AddChargeAdditionalInfoValidator'.format(ADDITIONAL_INFO_PATH))
    def test_additional_info_post_validation_error_with_source_permissions(self, mock_validator,
                                                                           get_source_information_list):
        mock_validator.validate.return_value.errors = [{'field': 'validation error'}]
        self.mock_session.return_value.add_charge_state = ADD_CHARGE_STATE
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc, Permissions.view_source_information]

        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        response = self.client.post(url_for('modify_land_charge.post_additional_info'), data={
            'additional-info': '',
            'reference': 'e',
        })

        get_source_information_list.assert_called()

        self.assertStatus(response, 400)
        self.assert_template_used('additional_info.html')

    def test_additional_info_post_without_session(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        self.mock_session.return_value.add_charge_state = None

        try:
            response = self.client.post(url_for('modify_land_charge.post_additional_info'), data=VALID_DATA)
        except Exception:
            self.assertStatus(response, 302)
            self.assert_redirects(response, '/error')

    @patch('{}.AddChargeAdditionalInfoValidator'.format(ADDITIONAL_INFO_PATH))
    def test_additional_info_post_exception(self, mock_validator):
        mock_validator.validate.side_effect = Exception('test exception')

        self.mock_session.return_value.add_charge_state = ADD_CHARGE_STATE
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        response = self.client.post(url_for('modify_land_charge.post_additional_info'), data={
            'additional-info': '',
            'reference': 'e',
        })

        self.assertStatus(response, 302)
        self.assert_redirects(response, '/error')

    def test_additional_info_get_with_session(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        response = self.client.get(url_for('modify_land_charge.get_additional_info'))
        self.assertStatus(response, 200)
        self.assert_template_used('additional_info.html')

    @patch('{}.get_source_information_list'.format(ADDITIONAL_INFO_PATH))
    def test_additional_info_get_with_session_source_permissions(self, get_source_information_list):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc, Permissions.view_source_information]

        response = self.client.get(url_for('modify_land_charge.get_additional_info'))

        get_source_information_list.assert_called()

        self.assertStatus(response, 200)
        self.assert_template_used('additional_info.html')

    def test_additional_info_get_without_session(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        self.mock_session.return_value.add_charge_state = None

        response = self.client.get(url_for('modify_land_charge.get_additional_info'))
        self.assertStatus(response, 302)
        self.assert_redirects(response, '/error')

    @patch('{}.render_template'.format(ADDITIONAL_INFO_PATH))
    def test_additional_info_render_exception(self, mock_render):
        self.mock_session.return_value.add_charge_state = ADD_CHARGE_STATE
        mock_render.side_effect = Exception('test exception')
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        response = self.client.get(url_for('modify_land_charge.get_additional_info'))
        self.assertStatus(response, 302)
        self.assertRedirects(response, "/error")
