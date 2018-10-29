from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.constants.permissions import Permissions
from flask import url_for
from unittest.mock import patch, PropertyMock, call

FINANCIAL_CHARGE_DETAILS_PATH = 'maintain_frontend.add_land_charge.financial_charge_details'


class TestFinancialChargeDetails(TestCase):

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_get_financial_charge_details_success(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_financial_charge_details'))

        self.assert_status(response, 200)
        self.assert_template_used('financial_charge_details.html')

    def test_get_financial_charge_details_success_with_interest(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        state.rate_of_interest = '5.1'

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_financial_charge_details'))

        self.assert_status(response, 200)
        self.assert_template_used('financial_charge_details.html')
        self.assertEqual(self.get_context_variable('request_body')['interest-paid-indicator'], 'Yes')
        self.assertEqual(self.get_context_variable('request_body')['interest-rate'], '5.1')

    def test_get_financial_charge_details_add_charge_state_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_financial_charge_details'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('{}.g'.format(FINANCIAL_CHARGE_DETAILS_PATH))
    def test_get_financial_charge_details_exception(self, mock_g):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        raise_exception = PropertyMock(side_effect=Exception('test exception'))
        type(mock_g).session = raise_exception

        try:
            response = self.client.get(url_for('add_land_charge.get_financial_charge_details'))
        except Exception:
            self.assertStatus(response, 302)
            self.assertRedirects(response, url_for("add_land_charge.new"))

    def test_get_financial_charge_details_no_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = []

        response = self.client.get(url_for('add_land_charge.get_financial_charge_details'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')

    @patch('{}.ReviewRouter'.format(FINANCIAL_CHARGE_DETAILS_PATH))
    def test_post_financial_charge_details_success_no_interest(self, mock_review_router):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        mock_review_router.get_redirect_url.return_value = url_for('add_land_charge.get_charge_description')

        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_financial_charge_details'),
                                    data={'amount-secured': '100.50', 'interest-paid-indicator': 'No',
                                          'interest-rate': ''})

        calls = [call('amount_originally_secured', '100.50'), call('rate_of_interest', "No interest is payable")]
        mock_review_router.update_edited_field.assert_has_calls(calls)

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_charge_description'))

    @patch('{}.ReviewRouter'.format(FINANCIAL_CHARGE_DETAILS_PATH))
    def test_post_financial_charge_details_success_with_interest(self, mock_review_router):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        mock_review_router.get_redirect_url.return_value = url_for('add_land_charge.get_charge_description')

        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_financial_charge_details'),
                                    data={'amount-secured': '100.50', 'interest-paid-indicator': 'Yes',
                                          'interest-rate': '5.11'})

        calls = [call('amount_originally_secured', '100.50'), call('rate_of_interest', '5.11')]
        mock_review_router.update_edited_field.assert_has_calls(calls)

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_charge_description'))

    def test_post_financial_charge_details_add_charge_state_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_financial_charge_details'),
                                    data={'amount-secured': '100', 'interest-paid-indicator': 'No'})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    def test_post_financial_charge_details_min_required_validation(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_financial_charge_details'),
                                    data={'amount-secured': '', 'interest-paid-indicator': ''})

        self.assert_status(response, 400)
        self.assert_template_used('financial_charge_details.html')
        self.assertIn('Amount is required', response.data.decode())
        self.assertIn('Choose one option', response.data.decode())

    def test_post_financial_charge_details_fail_validation_interest_required(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_financial_charge_details'),
                                    data={'amount-secured': '100', 'interest-paid-indicator': 'Yes',
                                          'interest-rate': ''})

        self.assert_status(response, 400)
        self.assert_template_used('financial_charge_details.html')
        self.assertIn('Interest is required', response.data.decode())

    def test_post_financial_charge_details_fail_validation_invalid_amount_and_interest(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_financial_charge_details'),
                                    data={'amount-secured': '100.123', 'interest-paid-indicator': 'Yes',
                                          'interest-rate': ''})

        self.assert_status(response, 400)
        self.assert_template_used('financial_charge_details.html')
        self.assertIn('Amount must be a positive number with up to 2 decimal places', response.data.decode())
        self.assertIn('Interest is required', response.data.decode())

    def test_post_financial_charge_details_no_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = []

        response = self.client.get(url_for('add_land_charge.post_financial_charge_details'),
                                   data={'amount-secured': '100', 'interest-paid-indicator': 'No'})

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')
