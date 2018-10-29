from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from flask import url_for
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.constants.permissions import Permissions
import json


class TestEditLocationConfirmation(TestCase):

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_edit_location_confirmation_renders_correct_template(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = 'abc'
        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.get(url_for('modify_land_charge.get_location_confirmation'))

        self.assert_status(response, 200)
        self.assert_template_used('edit_location_confirmation.html')

    def test_edit_get_location_confirmation_redirects_to_error_if_no_geometry(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = None
        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.get(url_for('modify_land_charge.get_location_confirmation'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/error')

    def test_edit_get_location_confirmation_redirects_to_error_if_state_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.get(url_for('modify_land_charge.get_location_confirmation'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/error')

    def test_edit_location_confirmation_post_redirects_to_error_if_state_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.post(url_for('modify_land_charge.post_location_confirmation'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/error')

    def test_edit_location_confirmation_post_redirects_to_error_if_no_geometry(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = None
        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.post(url_for('modify_land_charge.post_location_confirmation'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/error')

    def test_edit_location_confirmation_post_returns_required_validation(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = 'abc'

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.post(url_for('modify_land_charge.post_location_confirmation'),
                                    data={'location-confirmation': None})

        self.assert_status(response, 400)
        self.assert_template_used('edit_location_confirmation.html')
        self.assertIn('Confirm that you have the authority to update this charge', response.data.decode())

    def test_edit_location_confirmation_post_redirects_when_valid(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.roles = ['LLC LR Admins']
        state = LocalLandChargeItem()
        state.geometry = 'abc'
        state.local_land_charge = 12345678
        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        geometry = {'coordinates': [294230.7392612094, 93185.05361812815], 'type': 'Point'}
        form_data = {'saved-features': json.dumps({'features': [{'geometry': geometry}]})}
        response = self.client.post(url_for('modify_land_charge.post_location'), data=form_data)

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('modify_land_charge.modify_land_charge', local_land_charge='LLC-FCDPP'))
