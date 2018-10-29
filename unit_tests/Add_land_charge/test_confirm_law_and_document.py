from maintain_frontend import main
from flask import url_for
from flask_testing import TestCase
from unittest.mock import patch, call
from unit_tests.utilities import Utilities
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.constants.permissions import Permissions


class TestConfirmLawAndDocument(TestCase):

    def create_app(self):
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    @patch('maintain_frontend.add_land_charge.confirm_law_and_document.current_app')
    def test_get_redirects_to_new_when_state_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_law_document_confirmation'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.confirm_law_and_document.current_app')
    def test_get_redirects_to_new_when_charge_type_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_law_document_confirmation'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.confirm_law_and_document.current_app')
    def test_get_redirects_to_new_when_statutory_provision_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_law_document_confirmation'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    def test_get_successful(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"
        state.statutory_provision = "test statutory provision"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_law_document_confirmation'))

        self.assert_status(response, 200)
        self.assert_template_used('confirm_law_and_document.html')
        self.assertIn("test statutory provision", response.data.decode())

    def test_get_successful_with_instrument(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"
        state.statutory_provision = "test statutory provision"
        state.instrument = "test instrument"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_law_document_confirmation'))

        self.assert_status(response, 200)
        self.assert_template_used('confirm_law_and_document.html')
        self.assertIn("test statutory provision", response.data.decode())
        self.assertIn("test instrument", response.data.decode())

    @patch('maintain_frontend.add_land_charge.confirm_law_and_document.current_app')
    def test_confirm_redirects_to_new_when_state_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.law_document_confirmed'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.confirm_law_and_document.current_app')
    def test_confirm_redirects_to_new_when_charge_type_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.law_document_confirmed'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.confirm_law_and_document.current_app')
    def test_confirm_redirects_to_new_when_statutory_provision_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.law_document_confirmed'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    def test_confirm_successful(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"
        state.statutory_provision = "test statutory provision"
        state.instrument = "test instrument"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.law_document_confirmed'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_charge_date'))

    def test_confirm_successful_financial(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Financial"
        state.statutory_provision = "test statutory provision"
        state.instrument = "test instrument"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.law_document_confirmed'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_financial_charge'))

    def test_confirm_successful_land_compensation(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Land compensation"
        state.statutory_provision = "test statutory provision"
        state.instrument = "test instrument"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.law_document_confirmed'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_land_compensation_type'))

    def test_confirm_successful_lon(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Light obstruction notice"
        state.statutory_provision = "test statutory provision"
        state.instrument = "test instrument"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.law_document_confirmed'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_lon.new'))
