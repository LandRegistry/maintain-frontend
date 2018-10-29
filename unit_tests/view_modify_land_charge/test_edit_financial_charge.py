from maintain_frontend import main
from flask import url_for
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.constants.permissions import Permissions

HTML = 'financial_charge_details.html'


class TestEditFinancialCharge(TestCase):
    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def test_get_with_financial_charge(self):
        """should respond with a 200 and render the expected template"""
        charge = LocalLandChargeItem()
        charge.amount_originally_secured = '150000'
        charge.rate_of_interest = '5.5'
        self.mock_session.return_value.add_charge_state = charge
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.get(url_for('modify_land_charge.get_financial_charge'))

        self.status = self.assert_status(response, 200)
        self.assert_template_used(HTML)

    def test_get_with_financial_interest_maybe(self):
        """should respond with a 200 and render the expected template"""
        charge = LocalLandChargeItem()
        charge.amount_originally_secured = '150000'
        charge.rate_of_interest = 'Interest may be payable'
        self.mock_session.return_value.add_charge_state = charge
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.get(url_for('modify_land_charge.get_financial_charge'))

        self.status = self.assert_status(response, 200)
        self.assert_template_used(HTML)

    def test_post_redirects_to_error_when_state_is_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        self.mock_session.return_value.add_charge_state = None

        response = self.client.post(url_for('modify_land_charge.post_financial_charge'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/error')

    def test_get_redirects_to_error_when_state_is_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        self.mock_session.return_value.add_charge_state = None

        response = self.client.get(url_for('modify_land_charge.get_financial_charge'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/error')

    def test_post_financial_charge_fail_validation_invalid_amount_and_interest(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.post(url_for('modify_land_charge.post_financial_charge'),
                                    data={'amount-secured': '100.155', 'interest-paid-indicator': 'Yes',
                                          'interest-rate': ''})

        # self.assertRedirects(response, '')
        self.assert_status(response, 400)
        self.assert_template_used(HTML)
        self.assertIn('Amount must be a positive number with up to 2 decimal places', response.data.decode())
        self.assertIn('Interest is required', response.data.decode())

    def test_post_financial_charge_details_success_with_interest(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        state.local_land_charge = 1

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.post(url_for('modify_land_charge.post_financial_charge'),
                                    data={'amount-secured': '100.50', 'interest-paid-indicator': 'Yes',
                                          'interest-rate': '5.11'})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('modify_land_charge.modify_land_charge', local_land_charge="LLC-1"))

    def test_post_success_no_interest(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.local_land_charge = 1

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.post(url_for('modify_land_charge.post_financial_charge'),
                                    data={'interest-paid-indicator': 'No', 'amount-secured': '500'})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('modify_land_charge.modify_land_charge', local_land_charge="LLC-1"))

    def test_post_success_maybe_interest(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.local_land_charge = 1

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.post(url_for('modify_land_charge.post_financial_charge'),
                                    data={'interest-paid-indicator': 'Maybe', 'amount-secured': '500'})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('modify_land_charge.modify_land_charge', local_land_charge="LLC-1"))
