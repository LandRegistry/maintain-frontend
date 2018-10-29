from maintain_frontend import main
from flask_testing import TestCase as TestCase
from unit_tests.utilities import Utilities
from unittest.mock import patch, PropertyMock, call
from flask import url_for
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.constants.permissions import Permissions

ADD_CHARGE_STATE = LocalLandChargeItem()
ADDITIONAL_INFO_PATH = 'maintain_frontend.add_land_charge.additional_info'
VALID_DATA = {
    'additional-info': 'some info',
    'reference': '',
}


class TestAdditionalInfoView(TestCase):
    render_templates = False

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    @patch('{}.LocalAuthorityService'.format(ADDITIONAL_INFO_PATH))
    @patch('{}.ReviewRouter'.format(ADDITIONAL_INFO_PATH))
    @patch('{}.AddChargeAdditionalInfoValidator'.format(ADDITIONAL_INFO_PATH))
    def test_additional_info_post_success(self, mock_validator, mock_review_router, mock_authority_service):
        mock_validator.validate.return_value.errors = []
        mock_review_router.get_redirect_url.return_value = url_for('add_land_charge.get_review')

        self.mock_session.return_value.add_charge_state = ADD_CHARGE_STATE
        self.mock_session.return_value.add_charge_state.geometry = "abc"
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        response = self.client.post(url_for('add_land_charge.post_additional_info'), data=VALID_DATA)

        mock_review_router.update_edited_field.assert_has_calls([
            call('further_information_location', VALID_DATA['additional-info'])
        ])

        mock_authority_service.return_value.get_source_information_for_organisation.assert_not_called()
        self.assertStatus(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_review'))

    @patch('{}.LocalAuthorityService'.format(ADDITIONAL_INFO_PATH))
    @patch('{}.AddChargeAdditionalInfoValidator'.format(ADDITIONAL_INFO_PATH))
    def test_additional_info_post_validation_error_with_source_permissions(self, mock_validator,
                                                                           mock_authority_service):
        mock_validator.validate.return_value.errors = [{'field': 'validation error'}]
        self.mock_session.return_value.add_charge_state = ADD_CHARGE_STATE
        self.mock_session.return_value.user.permissions = [Permissions.add_llc, Permissions.view_source_information]
        self.mock_session.return_value.user.organisation = 'test org'

        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        response = self.client.post(url_for('add_land_charge.post_additional_info'), data={
            'additional-info': '',
            'reference': 'e',
        })

        mock_authority_service.return_value.get_source_information_for_organisation.assert_called('test org')

        self.assertStatus(response, 400)
        self.assert_template_used('additional_info.html')

    @patch('{}.LocalAuthorityService'.format(ADDITIONAL_INFO_PATH))
    @patch('{}.AddChargeAdditionalInfoValidator'.format(ADDITIONAL_INFO_PATH))
    def test_additional_info_post_validation_error(self, mock_validator, mock_authority_service):
        mock_validator.validate.return_value.errors = [{'field': 'validation error'}]
        self.mock_session.return_value.add_charge_state = ADD_CHARGE_STATE
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        response = self.client.post(url_for('add_land_charge.post_additional_info'), data={
            'additional-info': '',
            'reference': 'e',
        })

        mock_authority_service.return_value.get_source_information_for_organisation.assert_not_called()

        self.assertStatus(response, 400)
        self.assert_template_used('additional_info.html')

    def test_additional_info_post_without_session(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.add_charge_state = None

        try:
            response = self.client.post(url_for('add_land_charge.post_additional_info'), data=VALID_DATA)
        except Exception:
            self.assertStatus(response, 302)
            self.assertRedirects(response, url_for("add_land_charge.new"))

    @patch('{}.AddChargeAdditionalInfoValidator'.format(ADDITIONAL_INFO_PATH))
    def test_additional_info_post_exception(self, mock_validator):
        mock_validator.validate.side_effect = Exception('test exception')

        self.mock_session.return_value.add_charge_state = ADD_CHARGE_STATE
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        response = self.client.post(url_for('add_land_charge.post_additional_info'), data={
            'additional-info': '',
            'reference': 'e',
        })

        self.assertStatus(response, 302)
        self.assert_redirects(response, '/error')

    def test_additional_info_get_with_session(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_additional_info'))
        self.assertStatus(response, 200)
        self.assert_template_used('additional_info.html')

    @patch('{}.LocalAuthorityService'.format(ADDITIONAL_INFO_PATH))
    def test_additional_info_get_with_session_source_permissions(self, mock_authority_service):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.add_llc, Permissions.view_source_information]
        self.mock_session.return_value.user.organisation = 'test org'

        response = self.client.get(url_for('add_land_charge.get_additional_info'))
        mock_authority_service.return_value.get_source_information_for_organisation.assert_called_with('test org')

        self.assertStatus(response, 200)
        self.assert_template_used('additional_info.html')

    def test_additional_info_get_without_session(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_additional_info'))
        self.assertStatus(response, 302)
        self.assertRedirects(response, url_for("add_land_charge.new"))

    @patch('{}.g'.format(ADDITIONAL_INFO_PATH))
    def test_additional_info_get_session_exception(self, mock_g):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        raise_exception = PropertyMock(side_effect=Exception('test exception'))
        type(mock_g).session = raise_exception

        try:
            response = self.client.get(url_for('add_land_charge.get_additional_info'))
        except Exception:
            self.assertStatus(response, 302)
            self.assertRedirects(response, url_for("add_land_charge.new"))

    def test_additional_info_get_no_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = []

        response = self.client.get(url_for('add_land_charge.get_additional_info'))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')

    def test_additional_info_post_no_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = []

        response = self.client.post(url_for('add_land_charge.post_additional_info'))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')
