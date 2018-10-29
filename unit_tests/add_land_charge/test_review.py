from maintain_frontend import main
from flask import url_for
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from unittest.mock import patch, call
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.models import LocalLandChargeItem
import json

ADD_CHARGE_STATE = LocalLandChargeItem()
EDITED_FIELDS = []

VALID_PERMISSIONS = [Permissions.add_llc]
INVALID_PERMISSIONS = []


class TestReviewLandCharge(TestCase):

    def create_app(self):
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    @patch('maintain_frontend.add_land_charge.review.ReviewMap')
    def test_get(self, mock_review_map):
        """Should set the redirect_route in session, and render the expected template with expected objects."""
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.add_charge_state = ADD_CHARGE_STATE
        self.mock_session.return_value.edited_fields = EDITED_FIELDS
        self.mock_session.return_value.user.permissions = VALID_PERMISSIONS

        response = self.client.get(url_for('add_land_charge.get_review'))

        self.assert_status(response, 200)
        self.assert_template_used('review.html')

        self.assertEqual(self.mock_session.return_value.redirect_route, 'add_land_charge.get_review')

        self.assertEqual(self.get_context_variable('add_charge_state'), ADD_CHARGE_STATE)
        self.assertEqual(self.get_context_variable('edited_fields'), EDITED_FIELDS)
        self.assertEqual(self.get_context_variable('geometry'), json.dumps(ADD_CHARGE_STATE.geometry))
        self.assertEqual(self.get_context_variable('map'), mock_review_map)

    def test_get_redirects_to_new_when_state_is_none(self):
        """Should redirect to the start of the add flow if the add_land_charge state is not set in session."""
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = VALID_PERMISSIONS

        response = self.client.get(url_for('add_land_charge.get_review'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.review.AuditAPIService')
    @patch('maintain_frontend.add_land_charge.review.MaintainApiService')
    def test_post(self, mock_api_service, mock_audit):
        """Should call the API to persist the local land charge and reset the session values.


        If successful should then redirect to the confirmation page.
        """
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = VALID_PERMISSIONS
        self.mock_session.return_value.add_charge_state = ADD_CHARGE_STATE
        self.mock_session.return_value.add_charge_state.local_land_charge = '1'
        self.mock_session.return_value.charge_added_outside_users_authority = False

        response = self.client.post(url_for('add_land_charge.post_review'))

        mock_api_service.add_charge.assert_called_with(ADD_CHARGE_STATE)

        self.assertIsNone(self.mock_session.return_value.redirect_route)
        self.assertEqual(self.mock_session.return_value.edited_fields, [])
        expected_calls = [
            call("Submitting the charge", supporting_info=self.mock_session.return_value.add_charge_state.to_json()),
            call("Charge created", supporting_info={
                'id': self.mock_session.return_value.last_created_charge.charge_id})
        ]
        mock_audit.audit_event.assert_has_calls(expected_calls)

        for calls in mock_audit.mock_calls:
            self.assertNotEqual(calls[1], "Charge added outside users authority.")

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_confirmation'))

    @patch('maintain_frontend.add_land_charge.review.AuditAPIService')
    @patch('maintain_frontend.add_land_charge.review.request')
    @patch('maintain_frontend.add_land_charge.review.MaintainApiService')
    def test_post_multiple_submissions(self, mock_api_service, mock_request, mock_audit):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = VALID_PERMISSIONS
        self.mock_session.return_value.add_charge_state = ADD_CHARGE_STATE
        self.mock_session.return_value.submit_token = "previous-token"

        mock_request.form = {"csrf_token": "new-token"}
        response = self.client.post(url_for('add_land_charge.post_review'))
        second_response = self.client.post(url_for('add_land_charge.post_review'))

        mock_api_service.add_charge.assert_called_with(ADD_CHARGE_STATE)
        mock_api_service.add_charge.assert_called_once()

        self.assertIsNone(self.mock_session.return_value.redirect_route)
        self.assertEqual(self.mock_session.return_value.edited_fields, [])
        self.assertEqual(self.mock_session.return_value.submit_token, "new-token")

        self.assert_status(response, 302)
        self.assert_status(second_response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_confirmation'))
        self.assertRedirects(second_response, url_for('add_land_charge.get_confirmation'))

    def test_post_redirects_to_new_when_state_is_none(self):
        """Should reset the session values and redirect to the start of the flow if the add_land_charge state is not"""
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = VALID_PERMISSIONS

        response = self.client.post(url_for('add_land_charge.post_review'))

        self.assertIsNone(self.mock_session.return_value.redirect_route)
        self.assertEqual(self.mock_session.return_value.edited_fields, [])

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    def test_get_no_permission(self):
        """Should respond with a 302 and redirect to the not-authorised page if permissions are not set."""
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = INVALID_PERMISSIONS

        response = self.client.get(url_for('add_land_charge.post_review'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')

    def test_post_no_permission(self):
        """Should respond with a 302 and redirect to the not-authorised page if permissions are not set."""
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = INVALID_PERMISSIONS

        response = self.client.post(url_for('add_land_charge.post_review'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')

    @patch('maintain_frontend.add_land_charge.review.AuditAPIService')
    @patch('maintain_frontend.add_land_charge.review.request')
    @patch('maintain_frontend.add_land_charge.review.MaintainApiService')
    def test_post_audit_when_user_adds_charge_outside_authority(self, mock_api_service, mock_request, mock_audit):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = VALID_PERMISSIONS
        self.mock_session.return_value.add_charge_state = ADD_CHARGE_STATE
        self.mock_session.return_value.charge_added_outside_users_authority = True

        response = self.client.post(url_for('add_land_charge.post_review'))

        self.assert_status(response, 302)
        supporting_info = {
            'originating-authority': self.mock_session.return_value.user.organisation,
            'id': self.mock_session.return_value.last_created_charge.charge_id
        }
        expected_call = [call('Charge added outside users authority.', supporting_info=supporting_info)]
        mock_audit.audit_event.assert_has_calls(expected_call)
        self.assertIsNone(self.mock_session.return_value.charge_added_outside_users_authority)
