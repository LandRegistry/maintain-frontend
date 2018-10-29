from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from unittest.mock import patch
from flask import url_for
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.constants.permissions import Permissions
import json


GET_ADDRESS_CONFIRMATION = 'add_land_charge.get_address_confirmation'
POST_ADDRESS_CONFIRMATION = 'add_land_charge.post_address_confirmation'
NEXT_URL = 'add_land_charge.get_expiry'
TEMPLATE = 'address_confirmation.html'


class TestAddressConfirmation(TestCase):

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_address_confirmation_redirects_to_new(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for(GET_ADDRESS_CONFIRMATION))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    def test_address_confirmation_renders(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        previously_selected_address = {"address": "previously selected address"}

        state = LocalLandChargeItem()
        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.previously_selected_address = previously_selected_address
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for(GET_ADDRESS_CONFIRMATION))

        self.assertStatus(response, 200)
        self.assert_template_used(TEMPLATE)
        self.assertIn(previously_selected_address["address"], response.data.decode())

    def test_get_no_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = []

        response = self.client.get(url_for(GET_ADDRESS_CONFIRMATION))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')

    def test_post_no_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = []

        response = self.client.post(url_for(POST_ADDRESS_CONFIRMATION))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')

    @patch('maintain_frontend.add_land_charge.address_confirmation.AddressConverter')
    def test_post_yes_selected_successful(self, mock_address_converter):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        selected_address = {
            'address': 'display address',
            'line_1': 'Flat 1',
            'line_2': 'Place',
            'line_3': 'Holder',
            'line_4': 'Flat 1',
            'line_5': 'Flat 1',
            'line_6': 'Flat 1',
            'postcode': 'postcode',
            'uprn': 123456789
        }

        mock_address_converter.to_charge_address.return_value = selected_address

        response = self.client.post(url_for(POST_ADDRESS_CONFIRMATION), data={
            'has-address': 'Yes',
            'selected-address': json.dumps(selected_address)
        })

        session_charge_state = self.mock_session.return_value.add_charge_state

        self.assertEqual(session_charge_state.charge_address, selected_address)
        self.assertIsNone(session_charge_state.charge_geographic_description)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for(NEXT_URL))

    @patch('maintain_frontend.add_land_charge.address_confirmation.AddressConverter')
    def test_post_selected_address_successful(self, mock_address_converter):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        selected_address = {
            'address': 'display address',
            'line_1': 'Flat 1',
            'line_2': 'Place',
            'line_3': 'Holder',
            'line_4': 'Flat 1',
            'line_5': 'Flat 1',
            'line_6': 'Flat 1',
            'postcode': 'postcode',
            'uprn': 123456789
        }

        mock_address_converter.to_charge_address.return_value = selected_address

        response = self.client.post(url_for(POST_ADDRESS_CONFIRMATION), data={
            'has-address': 'ProvideAddress',
            'selected-address': json.dumps(selected_address)
        })

        session_charge_state = self.mock_session.return_value.add_charge_state

        self.assertEqual(session_charge_state.charge_address, selected_address)
        self.assertIsNone(session_charge_state.charge_geographic_description)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for(NEXT_URL))

    def test_post_location_description_successful(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        charge_geographic_description = 'This is a valid description'

        response = self.client.post(url_for(POST_ADDRESS_CONFIRMATION), data={
            'has-address': 'No',
            'charge-geographic-description': charge_geographic_description
        })

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for(NEXT_URL))

    def test_post_returns_choose_one_validation(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.previously_selected_address = None

        response = self.client.post(url_for(POST_ADDRESS_CONFIRMATION))

        self.assert_status(response, 400)
        self.assert_template_used(TEMPLATE)
        self.assertIn('Choose One', response.data.decode())

    def test_post_returns_select_address_validation(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.previously_selected_address = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for(POST_ADDRESS_CONFIRMATION), data={
            'has-address': 'ProvideAddress',
            'selected-address': None
        })

        self.assert_status(response, 400)
        self.assert_template_used(TEMPLATE)
        self.assertIn('Choose an address', response.data.decode())

    def test_post_returns_description_required_validation(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for(POST_ADDRESS_CONFIRMATION), data={
            'has-address': 'No',
            'charge-geographic-description': None
        })

        self.assert_status(response, 400)
        self.assert_template_used(TEMPLATE)
        self.assertIn('Describe the charge location', response.data.decode())

    def test_post_returns_description_length_validation(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for(POST_ADDRESS_CONFIRMATION), data={
            'has-address': 'No',
            'charge-geographic-description': 'a' * 1005
        })

        self.assert_status(response, 400)
        self.assert_template_used(TEMPLATE)
        self.assertIn('Answer is too long', response.data.decode())
