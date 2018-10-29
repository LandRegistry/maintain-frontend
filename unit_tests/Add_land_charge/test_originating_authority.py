from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.constants.permissions import Permissions
from flask import url_for
from unittest.mock import patch

ORIGINATING_AUTHORITY_PATH = 'maintain_frontend.add_land_charge.originating_authority'
ORIGINATING_AUTHORITY_GET = 'add_land_charge.get_originating_authority_page'
GET_AUTHORITIES = 'add_land_charge.get_originating_authority_page'
ORIGINATING_AUTHORITY_POST = 'add_land_charge.post_originating_authority_page'

ORIGINATING_AUTHORITIES = [
    'Authority A',
    'Authority B',
    'Authority C',
    'Authority D',
]
AUTHORITIES_JSON = [
    {'title': 'Authority A'}
]
PARTIAL_AUTHORITY = 'Auth A'
INVALID_AUTHORITY = ''


class TestOriginatingAuthority(TestCase):

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    @patch('{}.LocalAuthorityService'.format(ORIGINATING_AUTHORITY_PATH))
    def test_get_originating_authority_success(self, mock_authority_service):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for(ORIGINATING_AUTHORITY_GET))

        self.assert_status(response, 200)
        self.assert_template_used('originating_authority.html')

    def test_get_originating_authority_add_charge_state_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for(ORIGINATING_AUTHORITY_GET))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new_behalf_of_authority'))

    def test_get_originating_authority_adding_charge_for_other_authority_false(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.adding_charge_for_other_authority = False
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for(ORIGINATING_AUTHORITY_GET))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new_behalf_of_authority'))

    def test_get_originating_authority_no_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = []

        response = self.client.get(url_for(ORIGINATING_AUTHORITY_GET))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')

    @patch('{}.LocalAuthorityService'.format(ORIGINATING_AUTHORITY_PATH))
    @patch('{}.ReviewRouter'.format(ORIGINATING_AUTHORITY_PATH))
    def test_post_originating_authority_success(self, mock_review_router, mock_authority_service):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        mock_review_router.get_redirect_url.return_value = url_for('add_land_charge.get_charge_type')

        mock_authority_service.return_value.get_organisations.return_value = AUTHORITIES_JSON

        state = LocalLandChargeItem()
        self.mock_session.return_value.add_charge_state = state

        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for(ORIGINATING_AUTHORITY_POST),
                                    data={'authority-search-field': ORIGINATING_AUTHORITIES[0]})

        mock_review_router.update_edited_field.assert_called_with('originating_authority', ORIGINATING_AUTHORITIES[0])

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_charge_type'))

    @patch('{}.LocalAuthorityService'.format(ORIGINATING_AUTHORITY_PATH))
    def test_post_no_authority(self, mock_authority_service):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        state = LocalLandChargeItem()
        self.mock_session.return_value.add_charge_state = state

        mock_authority_service.return_value.get_authorities.return_value = ORIGINATING_AUTHORITIES

        response = self.client.post(url_for(ORIGINATING_AUTHORITY_POST),
                                    data={'authority-search-field': INVALID_AUTHORITY})

        self.assert_status(response, 400)
        self.assert_template_used('originating_authority.html')
        self.assertIn('Authority name is required', response.data.decode())

    @patch('{}.LocalAuthorityService'.format(ORIGINATING_AUTHORITY_PATH))
    def test_post_partial_authority(self, mock_authority_service):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        mock_authority_service.return_value.get_authorities.return_value = ORIGINATING_AUTHORITIES

        state = LocalLandChargeItem()
        self.mock_session.return_value.add_charge_state = state

        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for(ORIGINATING_AUTHORITY_POST),
                                    data={'authority-search-field': PARTIAL_AUTHORITY})

        self.assert_status(response, 400)
        self.assert_template_used('originating_authority.html')
        self.assertIn('No match found', response.data.decode())
