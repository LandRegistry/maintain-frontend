from maintain_frontend import main
from flask import url_for
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.constants.permissions import Permissions

HTML_OWNED = "land_compensation_owned.html"
HTML_PAYMENT = "land_compensation_payment.html"


class TestEditLandComparisonS52(TestCase):
    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def test_get_land_compensation_ownership(self):
        """should respond with a 200 and render the expected template"""
        charge = LocalLandChargeItem()
        charge.land_capacity_description = 'Freehold'
        self.mock_session.return_value.add_charge_state = charge
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.get(url_for('modify_land_charge.get_land_compensation_ownership'))

        self.status = self.assert_status(response, 200)
        self.assert_template_used(HTML_OWNED)

    def test_get_land_compensation_ownership_other(self):
        """should respond with a 200 and render the expected template"""
        charge = LocalLandChargeItem()
        charge.land_capacity_description = 'Tenure unknown'
        self.mock_session.return_value.add_charge_state = charge
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.get(url_for('modify_land_charge.get_land_compensation_ownership'))

        self.status = self.assert_status(response, 200)
        self.assert_template_used(HTML_OWNED)

    def test_get_land_compensation_payment(self):
        """should respond with a 200 and render the expected template"""
        charge = LocalLandChargeItem()
        charge.land_compensation_paid = '150000'
        charge.land_compensation_amount_type = 'Agreed amount'
        self.mock_session.return_value.add_charge_state = charge
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.get(url_for('modify_land_charge.get_land_compensation_payment'))

        self.status = self.assert_status(response, 200)
        self.assert_template_used(HTML_PAYMENT)

    def test_post_land_compensation_ownership(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        state.local_land_charge = 1
        state.land_capacity_description = 'Freehold'

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.post(url_for('modify_land_charge.post_land_compensation_ownership'),
                                    data={'land-owned-indicator': 'Leasehold', 'land-owned-other': None})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('modify_land_charge.modify_land_charge', local_land_charge="LLC-1"))

    def test_post_land_compensation_ownership_other(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        state.local_land_charge = 1
        state.land_capacity_description = 'Freehold'

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.post(url_for('modify_land_charge.post_land_compensation_ownership'),
                                    data={'land-owned-indicator': 'Other', 'land-owned-other': 'bobshold'})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('modify_land_charge.modify_land_charge', local_land_charge="LLC-1"))

    def test_post_land_compensation_ownership_other_change(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        state.local_land_charge = 1
        state.land_capacity_description = 'Bobshold'

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.post(url_for('modify_land_charge.post_land_compensation_ownership'),
                                    data={'land-owned-indicator': 'Freehold', 'land-owned-other': None})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('modify_land_charge.modify_land_charge', local_land_charge="LLC-1"))

    def test_post_land_compensation_ownership_other_amend(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        state.local_land_charge = 1
        state.land_capacity_description = 'Bobshold'

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.post(url_for('modify_land_charge.post_land_compensation_ownership'),
                                    data={'land-owned-indicator': 'Other', 'land-owned-other': 'Noddyhold'})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('modify_land_charge.modify_land_charge', local_land_charge="LLC-1"))

    def test_post_land_compensation_ownership_unchanged(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        state.local_land_charge = 1
        state.land_capacity_description = 'Freehold'

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.post(url_for('modify_land_charge.post_land_compensation_ownership'),
                                    data={'land-owned-indicator': 'Freehold', 'land-owned-other': None})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('modify_land_charge.modify_land_charge', local_land_charge="LLC-1"))

    def test_post_land_compensation_payment(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        state.local_land_charge = 1

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.post(url_for('modify_land_charge.post_land_compensation_payment'),
                                    data={'land-compensation-paid': '25000',
                                          'amount-of-compensation': '90000',
                                          'land-compensation-amount-type': 'Agreed amount'})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('modify_land_charge.modify_land_charge', local_land_charge="LLC-1"))

    def test_post_redirects_to_error_ownership_state_is_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        self.mock_session.return_value.add_charge_state = None

        response = self.client.post(url_for('modify_land_charge.post_land_compensation_ownership'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/error')

    def test_get_redirects_to_error_ownership_state_is_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        self.mock_session.return_value.add_charge_state = None

        response = self.client.get(url_for('modify_land_charge.get_land_compensation_ownership'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/error')

    def test_post_redirects_to_error_payment_state_is_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        self.mock_session.return_value.add_charge_state = None

        response = self.client.post(url_for('modify_land_charge.post_land_compensation_payment'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/error')

    def test_get_redirects_to_error_payment_state_is_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        self.mock_session.return_value.add_charge_state = None

        response = self.client.get(url_for('modify_land_charge.get_land_compensation_payment'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/error')

    def test_post_lca_ownership_fail_validation(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.post(url_for('modify_land_charge.post_land_compensation_ownership'),
                                    data={'land-ownership-indicator': None, 'land-ownership-other': None})

        # self.assertRedirects(response, '')
        self.assert_status(response, 400)
        self.assert_template_used(HTML_OWNED)
        self.assertIn('Choose one option', response.data.decode())

    def test_post_lca_payment_fail_validation(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.post(url_for('modify_land_charge.post_land_compensation_payment'),
                                    data={'land-compensation-paid': '', 'amount-of-compensation': '',
                                          'land-compensation-amount-type': ''})

        self.assert_status(response, 400)
        self.assert_template_used(HTML_PAYMENT)
        self.assertIn('Enter the advance payment', response.data.decode())
