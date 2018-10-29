from maintain_frontend import main
from flask_testing import TestCase
from flask import url_for
from unit_tests.utilities import Utilities
from unittest.mock import patch
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.constants.permissions import Permissions


class TestUpdateLocationConfirmation(TestCase):

    def create_app(self):
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def test_get_without_geom(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        state = LocalLandChargeItem()
        state.local_land_charge = 9372254
        state.geometry = None
        self.mock_session.return_value.add_charge_state = state

        response = self.client.get(url_for('modify_land_charge.get_update_location_confirmation'))
        self.assert_status(response, 302)
        self.assertRedirects(response, '/error')

    def test_get_without_state(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        self.mock_session.return_value.add_charge_state = None

        response = self.client.get(url_for('modify_land_charge.get_update_location_confirmation'))
        self.assert_status(response, 302)
        self.assertRedirects(response, '/error')

    def test_get_with_state(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        state = LocalLandChargeItem()
        state.local_land_charge = 9372254
        state.geometry = 'abc'
        self.mock_session.return_value.add_charge_state = state

        response = self.client.get(url_for('modify_land_charge.get_update_location_confirmation'))
        self.assert_status(response, 200)
        self.assert_template_used('update_location_confirmation.html')

    def test_post_without_geom(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        state = LocalLandChargeItem()
        state.local_land_charge = 9372254
        state.geometry = None
        self.mock_session.return_value.add_charge_state = state

        response = self.client.post(url_for('modify_land_charge.post_update_location_confirmation'))
        self.assert_status(response, 302)
        self.assertRedirects(response, '/error')

    def test_post_without_state(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        self.mock_session.return_value.add_charge_state = None

        response = self.client.post(url_for('modify_land_charge.post_update_location_confirmation'))
        self.assert_status(response, 302)
        self.assertRedirects(response, '/error')

    @patch('maintain_frontend.view_modify_land_charge.update_location_confirmation.LocationConfirmationValidator')
    def test_location_post_validation_errors(self, mock_location_validator):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.local_land_charge = 9372254

        self.mock_session.return_value.add_charge_state = state
        validation_errors = {'map': 'test error message'}
        mock_location_validator.validate.return_value.errors = validation_errors
        response = self.client.post(url_for('modify_land_charge.post_update_location_confirmation'))

        self.assert_status(response, 400)
        self.assert_template_used('update_location_confirmation.html')

    def test_post_success(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        self.mock_session.return_value.user.roles = ['LLC LR Admins']

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.local_land_charge = 399664232600384

        self.mock_session.return_value.add_charge_state = state
        form_data = {'location-confirmation': True}
        response = self.client.post(url_for('modify_land_charge.post_update_location_confirmation'), data=form_data)

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('modify_land_charge.modify_land_charge',
                                               local_land_charge='LLC-H3LL0W0RLD'))
