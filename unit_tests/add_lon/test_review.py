from maintain_frontend import main
from flask import url_for
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from unittest.mock import patch
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.models import LightObstructionNoticeItem
import json

ADD_CHARGE_STATE = LightObstructionNoticeItem()
EDITED_FIELDS = []
FILENAMES = {}

VALID_PERMISSIONS = [Permissions.add_lon]
INVALID_PERMISSIONS = []


class TestReviewLON(TestCase):

    def create_app(self):
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    @patch('maintain_frontend.add_lon.review.ReviewMap')
    def test_get(self, mock_review_map):
        """Should set the redirect_route in session, and render the expected template with expected objects."""
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.add_lon_charge_state = ADD_CHARGE_STATE
        self.mock_session.return_value.edited_fields = EDITED_FIELDS
        self.mock_session.return_value.user.permissions = VALID_PERMISSIONS
        self.mock_session.return_value.filenames = FILENAMES

        response = self.client.get(url_for('add_lon.get_review'))

        self.assert_status(response, 200)
        self.assert_template_used('review_lon.html')

        self.assertEqual(self.mock_session.return_value.redirect_route, 'add_lon.get_review')

        self.assertEqual(self.get_context_variable('add_lon_charge_state'), ADD_CHARGE_STATE)
        self.assertEqual(self.get_context_variable('edited_fields'), EDITED_FIELDS)
        self.assertEqual(self.get_context_variable('geometry'), json.dumps(ADD_CHARGE_STATE.geometry))
        self.assertEqual(self.get_context_variable('map'), mock_review_map)
        self.assertEqual(self.get_context_variable('filenames'), FILENAMES)

    def test_get_redirects_to_new_when_state_is_none(self):
        """Should redirect to the start of the add flow if the add_lon state is not set in session."""
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.add_lon_charge_state = None
        self.mock_session.return_value.user.permissions = VALID_PERMISSIONS

        response = self.client.get(url_for('add_lon.get_review'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_lon.new'))

    @patch('maintain_frontend.add_lon.review.AuditAPIService')
    @patch('maintain_frontend.add_lon.review.MaintainApiService')
    def test_post(self, mock_api_service, mock_audit):
        """Should call the API to persist the local land charge and reset the session values.


        If successful should then redirect to the confirmation page.
        """
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = VALID_PERMISSIONS
        self.mock_session.return_value.add_lon_charge_state = ADD_CHARGE_STATE

        response = self.client.post(url_for('add_lon.post_review'))

        mock_api_service.add_charge.assert_called_with(ADD_CHARGE_STATE)

        self.assertIsNone(self.mock_session.return_value.redirect_route)
        self.assertEqual(self.mock_session.return_value.edited_fields, {})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_lon.get_confirmation'))

    @patch('maintain_frontend.add_lon.review.AuditAPIService')
    @patch('maintain_frontend.add_lon.review.request')
    @patch('maintain_frontend.add_lon.review.MaintainApiService')
    def test_post_multiple_submissions(self, mock_api_service, mock_request, mock_audit):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = VALID_PERMISSIONS
        self.mock_session.return_value.add_lon_charge_state = ADD_CHARGE_STATE
        self.mock_session.return_value.submit_token = "previous-token"

        mock_request.form = {"csrf_token": "new-token"}
        response = self.client.post(url_for('add_lon.post_review'))
        second_response = self.client.post(url_for('add_lon.post_review'))

        mock_api_service.add_charge.assert_called_with(ADD_CHARGE_STATE)
        mock_api_service.add_charge.assert_called_once()

        self.assertIsNone(self.mock_session.return_value.redirect_route)
        self.assertEqual(self.mock_session.return_value.edited_fields, {})
        self.assertEqual(self.mock_session.return_value.submit_token, "new-token")

        self.assert_status(response, 302)
        self.assert_status(second_response, 302)
        self.assertRedirects(response, url_for('add_lon.get_confirmation'))
        self.assertRedirects(second_response, url_for('add_lon.get_confirmation'))

    def test_post_redirects_to_new_when_state_is_none(self):
        """Should reset the session values and redirect to the start of the flow if the add_lon state is not"""
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.add_lon_charge_state = None
        self.mock_session.return_value.user.permissions = VALID_PERMISSIONS

        response = self.client.post(url_for('add_lon.post_review'))

        self.assertIsNone(self.mock_session.return_value.redirect_route)
        self.assertEqual(self.mock_session.return_value.edited_fields, {})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_lon.new'))

    def test_get_no_permission(self):
        """Should respond with a 302 and redirect to the not-authorised page if permissions are not set."""
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = INVALID_PERMISSIONS

        response = self.client.get(url_for('add_lon.post_review'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')

    def test_post_no_permission(self):
        """Should respond with a 302 and redirect to the not-authorised page if permissions are not set."""
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = INVALID_PERMISSIONS

        response = self.client.post(url_for('add_lon.post_review'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')
