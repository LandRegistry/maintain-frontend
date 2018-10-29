from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from flask import url_for
from unittest.mock import patch
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LightObstructionNoticeItem

TEMPLATE = 'servient_structure_height.html'

ADD_LON = 'add_lon.'
GET_SERVIENT_STRUCTURE_HEIGHT = ADD_LON + 'get_servient_structure_height'
POST_SERVIENT_STRUCTURE_HEIGHT = ADD_LON + 'post_servient_structure_height'
GET_SERVIENT_STRUCTURE_POSITION = ADD_LON + 'get_servient_structure_position'

NO_VALIDATION_ERRORS = []
ERROR = {'measurement': ['Choose one']}


class TestLONServientStructureHeight(TestCase):
    def create_app(self):
        main.app.testing = True
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def test_servient_structure_height_redirects_to_new_when_state_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.add_lon_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        response = self.client.get(url_for(GET_SERVIENT_STRUCTURE_POSITION))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for(ADD_LON + 'new'))

    def test_servient_structure_height_get(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LightObstructionNoticeItem()
        self.mock_session.add_lon_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        response = self.client.get(url_for(GET_SERVIENT_STRUCTURE_HEIGHT))

        self.assert_status(response, 200)
        self.assert_template_used(TEMPLATE)

    @patch('maintain_frontend.add_lon.servient_structure_height.ReviewRouter')
    @patch('maintain_frontend.add_lon.servient_structure_height.ServientStructureHeightValidator')
    def test_servient_structure_height_unlimited_height_selected(self, mock_validator, mock_review_router):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        mock_review_router.get_redirect_url.return_value = url_for(GET_SERVIENT_STRUCTURE_POSITION)

        state = ()
        self.mock_session.add_lon_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        mock_validator.validate.return_value.errors = []
        response = self.client.post(url_for(POST_SERVIENT_STRUCTURE_HEIGHT))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for(GET_SERVIENT_STRUCTURE_POSITION))

    @patch('maintain_frontend.add_lon.servient_structure_height.ReviewRouter')
    @patch('maintain_frontend.add_lon.servient_structure_height.ServientStructureHeightValidator')
    def test_servient_structure_height_specific_height_selected(self, mock_validator, mock_review_router):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        mock_review_router.get_redirect_url.return_value = url_for(GET_SERVIENT_STRUCTURE_POSITION)

        state = LightObstructionNoticeItem()
        self.mock_session.add_lon_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        mock_validator.validate.return_value.errors = []
        response = self.client.post(url_for(POST_SERVIENT_STRUCTURE_HEIGHT))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for(GET_SERVIENT_STRUCTURE_POSITION))

    @patch('maintain_frontend.add_lon.servient_structure_height.ServientStructureHeightValidator')
    def test_servient_structure_height_no_select(self, mock_validator):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LightObstructionNoticeItem()
        self.mock_session.add_lon_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]
        mock_validator.validate.return_value.errors = ERROR

        response = self.client.post(url_for(POST_SERVIENT_STRUCTURE_HEIGHT))

        self.assert_context('validation_errors', ERROR)
        self.assert_status(response, 400)
        self.assert_template_used(TEMPLATE)
