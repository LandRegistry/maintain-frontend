from maintain_frontend import main
from flask import url_for
from flask_testing import TestCase
from unittest.mock import patch, call, MagicMock
from unit_tests.utilities import Utilities
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.constants.permissions import Permissions


class TestChargeType(TestCase):

    def create_app(self):
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    @patch('maintain_frontend.add_land_charge.charge_type.current_app')
    def test_get_charge_type_redirects_to_new_when_state_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_charge_type'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.charge_type.current_app')
    def test_post_charge_type_redirects_to_new_when_state_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_charge_type'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.charge_type.CategoryService')
    def test_get_charge_type_success(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"

        mock_service.get_categories.return_value = [
            {"name": "ABC", "display": "ABC Display"},
            {"name": "DEF", "display": "DEF Display"}
        ]

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_charge_type'))

        self.assert_status(response, 200)
        self.assert_template_used('charge_type.html')
        self.assertIn("ABC Display", response.data.decode())
        self.assertIn("DEF Display", response.data.decode())

    def test_get_no_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.user.permissions = []

        response = self.client.get(url_for('add_land_charge.get_charge_type'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')

    @patch('maintain_frontend.add_land_charge.charge_type.current_app')
    def test_post_success(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_charge_type'), data={
            'charge-type': 'ABC'
        })

        calls = [call("Updating session object with charge type: %s", "ABC")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_sub_category'))

    @patch('maintain_frontend.add_land_charge.charge_type.current_app')
    def test_post_success_update_type(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "def"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_charge_type'), data={
            'charge-type': 'ABC'
        })

        calls = [call("Updating session object with charge type: %s", "ABC")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_sub_category'))

    @patch('maintain_frontend.add_land_charge.charge_type.CategoryService')
    @patch('maintain_frontend.add_land_charge.charge_type.current_app')
    @patch('maintain_frontend.add_land_charge.charge_type.ChargeTypeValidator')
    def test_post_validation_errors(self, mock_charge_type_validator, mock_current_app, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        mock_service.return_value.get_categories.return_value = [
            {"name": "ABC", "display": "ABC Display"},
            {"name": "DEF", "display": "DEF Display"}
        ]

        mock_validation_errors = MagicMock()
        mock_validation_errors.errors = {'field_name': 'error'}
        mock_validation_errors.summary_heading_text = 'test'
        mock_charge_type_validator.validate.return_value = mock_validation_errors

        response = self.client.post(url_for('add_land_charge.post_charge_type'), data={
            'charge-type': ''
        })

        mock_current_app.logger.warning.assert_called_with('Validation errors occurred')
        self.assertStatus(response, 400)
