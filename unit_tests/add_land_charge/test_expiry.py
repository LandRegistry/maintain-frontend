from maintain_frontend import main
from flask import url_for
from flask_testing import TestCase
from unittest.mock import patch
from unit_tests.utilities import Utilities
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.constants.permissions import Permissions
from datetime import date

EXPIRED = 'yes'
INVALID_DAY = '1'
INVALID_MONTH = '1'
INVALID_YEAR = '2000'
EXPIRED_REQUEST = {
    'does_charge_expire': EXPIRED,
    'charge_expiry_day': INVALID_DAY,
    'charge_expiry_month': INVALID_MONTH,
    'charge_expiry_year': INVALID_YEAR
}

NOT_EXPIRED = 'no'
VALID_DAY = '1'
VALID_MONTH = '1'
VALID_YEAR = '2000'
NOT_EXPIRED_REQUEST = {
    'does_charge_expire': NOT_EXPIRED,
    'charge_expiry_day': VALID_DAY,
    'charge_expiry_month': VALID_MONTH,
    'charge_expiry_year': VALID_YEAR
}


class TestExpiry(TestCase):

    def create_app(self):
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_expiry_get(self):
        """should respond with a 200 and render the expected template with the expiry date from session if set."""
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.add_charge_state.expiry_date = \
            date(int(VALID_YEAR), int(VALID_MONTH), int(VALID_DAY))

        response = self.client.get(url_for('add_land_charge.get_expiry'))

        expected_request_body = {
            'charge_expiry_day': int(VALID_DAY),
            'charge_expiry_month': int(VALID_MONTH),
            'charge_expiry_year': int(VALID_YEAR),
            'does_charge_expire': EXPIRED
        }

        self.assert_status(response, 200)
        self.assert_template_used('expiry.html')
        self.assertEqual(self.get_context_variable('request_body'), expected_request_body)

    def test_expiry_redirects_to_new_when_state_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_expiry'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.expiry.ExpiryValidator')
    def test_expiry_post_validation_errors(self, mock_expiry_validator):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        validation_errors = {'does_charge_expire': 'test error message'}
        mock_expiry_validator.validate.return_value.errors = validation_errors
        response = self.client.post(url_for('add_land_charge.post_expiry'))

        self.assert_status(response, 400)
        self.assert_context('validation_errors', validation_errors)

    def test_expiry_post_redirects_to_new_when_state_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_expiry'), data={
            'does_charge_expire': 'no'
        })

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.expiry.ReviewRouter')
    def test_expiry_post_charge_does_not_expire(self, mock_review_router):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        mock_review_router.get_redirect_url.return_value = url_for('add_land_charge.get_additional_info')

        state = LocalLandChargeItem()
        state.geometry = "abc"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_expiry'), data={
            'does_charge_expire': 'no'
        })

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_additional_info'))

    @patch('maintain_frontend.add_land_charge.expiry.ReviewRouter')
    def test_expiry_post_dates(self, mock_review_router):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        mock_review_router.get_redirect_url.return_value = url_for('add_land_charge.get_additional_info')

        state = LocalLandChargeItem()
        state.geometry = "abc"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_expiry'), data=EXPIRED_REQUEST)

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_additional_info'))

    def test_get_no_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.user.permissions = []

        response = self.client.get(url_for('add_land_charge.get_expiry'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')

    def test_post_no_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.user.permissions = []

        response = self.client.post(url_for('add_land_charge.post_expiry'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')

    @patch('maintain_frontend.add_land_charge.expiry.ReviewRouter')
    def test_expiry_post_dates_not_used_if_does_not_expire(self, mock_review_router):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        mock_review_router.get_redirect_url.return_value = url_for('add_land_charge.get_additional_info')

        state = LocalLandChargeItem()
        state.geometry = "abc"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_expiry'), data=NOT_EXPIRED_REQUEST)

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_additional_info'))
        self.assertIsNone(self.mock_session.return_value.add_charge_state.expiry_date)

    def test_expiry_post_2_digit_year(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"

        data = {
            'does_charge_expire': 'yes',
            'charge_expiry_day': '01',
            'charge_expiry_month': '01',
            'charge_expiry_year': '01'
        }

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_expiry'), data=data)

        self.assert_status(response, 400)
        validation_errors = self.get_context_variable('validation_errors')
        self.assertIsNotNone(validation_errors)
        self.assertIsNotNone(validation_errors['charge_expiry_date'])
        self.assertEqual(validation_errors['charge_expiry_date'].summary_message, 'Date is invalid')
        self.assertEqual(validation_errors['charge_expiry_date'].inline_message, 'Year must be in the format YYYY')
