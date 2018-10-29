from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from flask import url_for
from unittest.mock import patch
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LightObstructionNoticeItem

TEMPLATE = 'applicant_info.html'

ADD_LON = 'add_lon.'
GET_APPLICANT_INFO = ADD_LON + 'get_applicant_info'
POST_APPLICANT_INFO = ADD_LON + 'post_applicant_info'
GET_DOMINANT_BUILDING = ADD_LON + 'get_dominant_building_info'

NO_VALIDATION_ERRORS = []
ERROR_MESSAGE = ['some error message']

INVALID_STRING = ""
VALID_STRING = "string"
VALID_POSTCODE = "EX4 7AN"


class TestLONApplicantInfo(TestCase):
    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_applicant_info_redirects_to_new_when_state_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.add_lon_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        response = self.client.get(url_for(GET_APPLICANT_INFO))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for(ADD_LON + 'new'))

    def test_applicant_info_get(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LightObstructionNoticeItem()
        self.mock_session.add_lon_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        response = self.client.get(url_for(GET_APPLICANT_INFO))

        self.assert_status(response, 200)
        self.assert_template_used(TEMPLATE)

    def test_applicant_info_no_permission_redirects(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.user.permissions = []

        response = self.client.get(url_for(GET_APPLICANT_INFO))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')

        response = self.client.post(url_for(POST_APPLICANT_INFO))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')

    @patch('maintain_frontend.add_lon.applicant_info.AddressConverter')
    @patch('maintain_frontend.add_lon.applicant_info.ReviewRouter')
    @patch('maintain_frontend.add_lon.applicant_info.ApplicantInfoValidator')
    def test_post_with_no_validation_errors(self, mock_validator, mock_review_router, mock_address_converter):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]
        mock_review_router.get_redirect_url.return_value = url_for(GET_DOMINANT_BUILDING)

        mock_validator.validate.return_value.errors = NO_VALIDATION_ERRORS

        mock_address_converter.condense_address.return_value = {'address_line_1': VALID_STRING}

        data = {
            'applicant_name': VALID_STRING,
            'postcode': VALID_POSTCODE,
            'address_line_1': VALID_STRING,
            'address_line_2': VALID_STRING,
            'address_line_3': VALID_STRING,
            'address_line_4': VALID_STRING,
            'address_line_5': VALID_STRING,
            'address_line_6': VALID_STRING,
            'country': VALID_STRING
        }

        response = self.client.post(url_for(POST_APPLICANT_INFO), data=data)

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for(GET_DOMINANT_BUILDING))

    @patch('maintain_frontend.add_lon.applicant_info.ApplicantInfoValidator')
    def test_post_with_validation_errors(self, mock_validator):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        name_error = {'applicant_name': ERROR_MESSAGE}
        mock_validator.validate.return_value.errors = name_error

        data = {
        }

        response = self.client.post(url_for(POST_APPLICANT_INFO), data=data)

        self.assert_context('validation_errors', name_error)
        self.assert_status(response, 400)
        self.assert_template_used(TEMPLATE)
