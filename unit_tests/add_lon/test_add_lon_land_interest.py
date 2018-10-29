from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from flask import url_for
from unittest.mock import patch
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LightObstructionNoticeItem

TEMPLATE = 'lon_land_interest.html'

ADD_LON = 'add_lon.'
GET_LAND_INTEREST = ADD_LON + 'get_land_interest'
POST_LAND_INTEREST = ADD_LON + 'post_land_interest'
GET_UPLOAD_LON_DOCUMENTS = ADD_LON + 'get_upload_lon_documents'

NO_VALIDATION_ERRORS = []
ERROR = {'servient-land-interest-description': ['Choose one']}


class TestLONLandInterest(TestCase):
    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_land_interest_redirects_to_new_when_state_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.add_lon_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        response = self.client.get(url_for(GET_LAND_INTEREST))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for(ADD_LON + 'new'))

    def test_land_interest_get(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LightObstructionNoticeItem()
        self.mock_session.add_lon_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        response = self.client.get(url_for(GET_LAND_INTEREST))

        self.assert_status(response, 200)
        self.assert_template_used(TEMPLATE)

    @patch('maintain_frontend.add_lon.lon_land_interest.ReviewRouter')
    def test_land_interest_owner_selected(self, mock_review_router):
        mock_review_router.get_redirect_url.return_value = url_for(GET_UPLOAD_LON_DOCUMENTS)
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LightObstructionNoticeItem()
        self.mock_session.add_lon_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        data = {'servient-land-interest-description': 'Owner'}
        response = self.client.post(url_for(POST_LAND_INTEREST), data=data)

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for(GET_UPLOAD_LON_DOCUMENTS))

    @patch('maintain_frontend.add_lon.lon_land_interest.ReviewRouter')
    def test_land_interest_tenant_selected(self, mock_review_router):
        mock_review_router.get_redirect_url.return_value = url_for(GET_UPLOAD_LON_DOCUMENTS)
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LightObstructionNoticeItem()
        self.mock_session.add_lon_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        data = {'servient-land-interest-description': 'Tenant'}
        response = self.client.post(url_for(POST_LAND_INTEREST), data=data)

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for(GET_UPLOAD_LON_DOCUMENTS))

    @patch('maintain_frontend.add_lon.lon_land_interest.ReviewRouter')
    def test_land_interest_lender_selected(self, mock_review_router):
        mock_review_router.get_redirect_url.return_value = url_for(GET_UPLOAD_LON_DOCUMENTS)
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LightObstructionNoticeItem()
        self.mock_session.add_lon_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        data = {'servient-land-interest-description': 'Lender'}
        response = self.client.post(url_for(POST_LAND_INTEREST), data=data)

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for(GET_UPLOAD_LON_DOCUMENTS))

    @patch('maintain_frontend.add_lon.lon_land_interest.ValidationErrorBuilder')
    def test_land_interest_no_select(self, mock_validator):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LightObstructionNoticeItem()
        self.mock_session.add_lon_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]
        mock_validator.return_value.errors = ERROR

        response = self.client.post(url_for(POST_LAND_INTEREST))

        self.assert_context('validation_errors', ERROR)
        self.assert_status(response, 400)
        self.assert_template_used(TEMPLATE)

    @patch('maintain_frontend.add_lon.lon_land_interest.request')
    @patch('maintain_frontend.add_lon.lon_land_interest.ValidationErrorBuilder')
    @patch('maintain_frontend.add_lon.lon_land_interest.render_template')
    def test_add_lon_land_interest_other_missing_details(self, mock_render_template, mock_validator, mock_request):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        mock_request.form.get.side_effect = ["Other", ""]
        mock_validator.return_value.errors = {"error": "test-error"}
        mock_render_template.return_value = "Template was called"

        response = self.client.post(url_for('add_lon.post_land_interest'))

        self.assert_status(response, 400)
        mock_render_template.assert_called()
