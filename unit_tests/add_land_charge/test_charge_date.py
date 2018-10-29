from maintain_frontend import main
from flask import url_for
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from unittest.mock import patch
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.constants.permissions import Permissions
from datetime import date

HTML = 'charge_date.html'

NO_VALIDATION_ERRORS = []
VALIDATION_ERRORS = {'date': ['some error message']}

VALID_DAY = '1'
VALID_MONTH = '1'
VALID_YEAR = '2001'
VALID_DATE = {
    "date-day": VALID_DAY,
    "date-month": VALID_MONTH,
    "date-year": VALID_YEAR
}

INVALID_DAY = 'some invalid day'
INVALID_MONTH = 'some invalid month'
INVALID_YEAR = 'some invalid year'
INVALID_DATE = {
    "date-day": INVALID_DAY,
    "date-month": INVALID_MONTH,
    "date-year": INVALID_YEAR
}


class TestChargeCreationDate(TestCase):

    def create_app(self):
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_get(self):
        """should respond with a 200 and render the expected template with the charge date from session if set."""
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.add_charge_state.charge_creation_date = \
            date(int(VALID_YEAR), int(VALID_MONTH), int(VALID_DAY))

        response = self.client.get(url_for('add_land_charge.get_charge_date'))

        expected_date = {
            'day': VALID_DAY,
            'month': VALID_MONTH,
            'year': VALID_YEAR
        }

        self.status = self.assert_status(response, 200)
        self.assert_template_used(HTML)
        self.assertEqual(self.get_context_variable('date'), expected_date)

    def test_get_redirects_to_new_when_state_is_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_charge_date'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.charge_date.ReviewRouter')
    @patch('maintain_frontend.add_land_charge.validation.charge_date_validator.ChargeDateValidator')
    def test_post_with_no_validation_errors(self, mock_validator, mock_review_router):
        """should respond with a 302 and redirect to the add_land_charge_date page."""
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        mock_review_router.get_redirect_url.return_value = url_for('add_land_charge.get_location')

        mock_validator.validate.return_value = NO_VALIDATION_ERRORS

        response = self.client.post(url_for('add_land_charge.post_charge_date'), data=VALID_DATE)

        mock_review_router.update_edited_field.assert_called_with(
            'charge_creation_date', date(int(VALID_YEAR), int(VALID_MONTH), int(VALID_DAY))
        )

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_location'))

    @patch('maintain_frontend.add_land_charge.charge_date.ChargeDateValidator')
    def test_post_with_validation_errors(self, mock_validator):
        """Should respond with a 200, render the expected template, and return the expected error object."""
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        mock_validator.validate.return_value.errors = VALIDATION_ERRORS

        response = self.client.post(url_for('add_land_charge.post_charge_date'), data=INVALID_DATE)

        mock_validator.validate.assert_called_with(INVALID_DAY, INVALID_MONTH, INVALID_YEAR)

        self.assert_status(response, 200)
        self.assert_template_used(HTML)
        self.assert_context('validation_errors', VALIDATION_ERRORS)

    def test_post_redirects_to_new_when_state_is_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_charge_date'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    def test_get_no_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = []

        response = self.client.get(url_for('add_land_charge.get_charge_date'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')

    def test_post_no_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = []

        response = self.client.post(url_for('add_land_charge.post_charge_date'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')
