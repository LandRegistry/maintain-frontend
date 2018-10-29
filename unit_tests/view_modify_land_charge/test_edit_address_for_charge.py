from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from flask import url_for
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.services import charge_id_services
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.constants.permissions import Permissions
import json


GET_ADDRESS_CONFIRMATION = 'modify_land_charge.get_address_for_charge'
POST_ADDRESS_CONFIRMATION = 'modify_land_charge.post_address_for_charge'
NEXT_URL = 'modify_land_charge.modify_land_charge'
TEMPLATE = 'address_for_charge.html'
VALID_DESCRIPTION = "Valid description"
VALID_ADDRESS = {
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


class TestEditAddressForCharge(TestCase):

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_address_for_charge_redirects_to_error(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.get(url_for(GET_ADDRESS_CONFIRMATION))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/error')

    def test_address_for_charge_renders_charge_address(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()

        charge_address = {
            'address': 'display address',
            'line-1': 'Flat 1',
            'line-2': 'Place',
            'line-3': 'Holder',
            'line-4': 'Flat 1',
            'line-5': 'Flat 1',
            'line-6': 'Flat 1',
            'postcode': 'postcode',
            'uprn': 123456789
        }

        state.charge_address = charge_address
        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.get(url_for(GET_ADDRESS_CONFIRMATION))

        self.assertStatus(response, 200)
        self.assert_template_used(TEMPLATE)

    def test_address_for_charge_renders_charge_description(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        state.charge_geographic_description = VALID_DESCRIPTION
        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.get(url_for(GET_ADDRESS_CONFIRMATION))

        self.assertStatus(response, 200)
        self.assert_template_used(TEMPLATE)

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

    def test_post_selected_address_successful(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        state.local_land_charge = 1
        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.post(url_for(POST_ADDRESS_CONFIRMATION), data={
            'has-address': 'ProvideAddress',
            'selected-address': json.dumps(VALID_ADDRESS)
        })

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for(NEXT_URL, local_land_charge=charge_id_services.calc_display_id(
                                               state.local_land_charge)))

    def test_post_location_description_successful(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        state.local_land_charge = 1
        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        charge_geographic_description = 'This is a valid description'

        response = self.client.post(url_for(POST_ADDRESS_CONFIRMATION), data={
            'has-address': 'No',
            'charge-geographic-description': charge_geographic_description
        })

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for(NEXT_URL, local_land_charge=charge_id_services.calc_display_id(
                                               state.local_land_charge)))

    def test_post_returns_choose_one_validation(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.post(url_for(POST_ADDRESS_CONFIRMATION))

        self.assert_status(response, 400)
        self.assert_template_used(TEMPLATE)
        self.assertIn('Choose One', response.data.decode())

    def test_post_returns_select_address_validation(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

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
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

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
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.post(url_for(POST_ADDRESS_CONFIRMATION), data={
            'has-address': 'No',
            'charge-geographic-description': 'a' * 1005
        })

        self.assert_status(response, 400)
        self.assert_template_used(TEMPLATE)
        self.assertIn('Answer is too long', response.data.decode())
