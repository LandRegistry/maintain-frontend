from maintain_frontend import main
from flask import url_for
from flask_testing import TestCase
from unittest.mock import patch, call, MagicMock
from unit_tests.utilities import Utilities
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.constants.permissions import Permissions


class TestLandCompensationType(TestCase):

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    @patch('maintain_frontend.add_land_charge.land_compensation_type.current_app')
    def test_get_land_compensation_type_redirects_to_new_when_state_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_land_compensation_type'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.land_compensation_type.current_app')
    def test_post_land_compensation_type_redirects_to_new_when_state_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_land_compensation_type'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    def test_get_land_compensation_type_success(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_land_compensation_type'))

        self.assert_status(response, 200)
        self.assert_template_used('land_compensation_type.html')

    def test_get_no_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.user.permissions = []

        response = self.client.get(url_for('add_land_charge.get_land_compensation_type'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')

    @patch('maintain_frontend.add_land_charge.land_compensation_type.current_app')
    @patch('maintain_frontend.add_land_charge.land_compensation_type.LandCompensationTypeValidator')
    def test_post_success_no(self, mock_land_compensation_type_validator, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        mock_validation_errors = MagicMock()
        mock_validation_errors.errors = {}
        mock_land_compensation_type_validator.validate.return_value = mock_validation_errors

        response = self.client.post(url_for('add_land_charge.post_land_compensation_type'), data={
            'advance-payment-known': 'No'
        })

        calls = [call("Endpoint called with advance-payment-known = '%s'", "No")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_land_compensation_land_sold'))

    @patch('maintain_frontend.add_land_charge.land_compensation_type.current_app')
    @patch('maintain_frontend.add_land_charge.land_compensation_type.LandCompensationTypeValidator')
    def test_post_success_yes(self, mock_land_compensation_type_validator, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        mock_validation_errors = MagicMock()
        mock_validation_errors.errors = {}
        mock_land_compensation_type_validator.validate.return_value = mock_validation_errors

        response = self.client.post(url_for('add_land_charge.post_land_compensation_type'), data={
            'advance-payment-known': 'Yes'
        })

        calls = [call("Endpoint called with advance-payment-known = '%s'", "Yes")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_land_compensation_payment'))

    def test_post_no_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.user.permissions = []

        response = self.client.post(url_for('add_land_charge.post_land_compensation_type'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')

    @patch('maintain_frontend.add_land_charge.land_compensation_type.current_app')
    @patch('maintain_frontend.add_land_charge.land_compensation_type.LandCompensationTypeValidator')
    def test_post_validation_errors(self, mock_land_compensation_type_validator, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        mock_validation_errors = MagicMock()
        mock_validation_errors.errors = {'field_name': 'error'}
        mock_validation_errors.summary_heading_text = 'test'
        mock_land_compensation_type_validator.validate.return_value = mock_validation_errors

        response = self.client.post(url_for('add_land_charge.post_land_compensation_type'), data={
            'advance-payment-known': ''
        })

        mock_current_app.logger.warning.assert_called_with('Validation errors occurred')
        self.assertStatus(response, 400)
