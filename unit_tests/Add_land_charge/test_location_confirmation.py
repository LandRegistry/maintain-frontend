from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from flask import url_for
from unittest.mock import patch
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.constants.permissions import Permissions


class TestLocationConfirmation(TestCase):

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_location_confirmation_redirects_to_new(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_location_confirmation'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    def test_location_confirmation_redirects_to_location_if_no_geometry(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = None
        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_location_confirmation'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_location'))

    def test_location_confirmation_renders_address_false(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = 'abc'
        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_location_confirmation', address_selected=False))

        self.assertStatus(response, 200)
        self.assert_template_used('location_confirmation.html')

    def test_location_confirmation_renders_address_true(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = 'abc'
        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_location_confirmation', address_selected=True))

        self.assertStatus(response, 200)
        self.assert_template_used('location_confirmation.html')

    def test_location_confirmation_post_redirects_to_new_when_state_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_location_confirmation'),
                                    data={'location-confirmation': True})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    def test_location_confirmation_post_redirects_to_location_when_geom_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = None
        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_location_confirmation'),
                                    data={'location-confirmation': True})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_location'))

    def test_location_confirmation_post_returns_required_validation(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = 'abc'

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_location_confirmation'),
                                    data={'location-confirmation': None})

        self.assert_status(response, 400)
        self.assert_template_used('location_confirmation.html')
        self.assertIn('Confirm that you have the authority to add this charge', response.data.decode())

    @patch('maintain_frontend.add_land_charge.location_confirmation.ReviewRouter')
    def test_location_confirmation_post_redirects_when_address_set(self, mock_review_router):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        mock_review_router.get_redirect_url.return_value = url_for('add_land_charge.get_address_for_charge')

        state = LocalLandChargeItem()
        state.geometry = 'abc'

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_location_confirmation', address_selected=True),
                                    data={'location-confirmation': True})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_address_for_charge'))
        self.assertTrue(self.mock_session.return_value.charge_added_outside_users_authority)

    @patch('maintain_frontend.add_land_charge.location_confirmation.ReviewRouter')
    def test_location_confirmation_post_redirects_when_address_not_set(self, mock_review_router):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        mock_review_router.get_redirect_url.return_value = url_for('add_land_charge.get_address_confirmation')

        state = LocalLandChargeItem()
        state.geometry = 'abc'

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_location_confirmation', address_selected=False),
                                    data={'location-confirmation': True})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_address_confirmation'))
        self.assertTrue(self.mock_session.return_value.charge_added_outside_users_authority)
