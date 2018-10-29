from maintain_frontend import main
from flask import url_for
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from unittest.mock import patch
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.constants.permissions import Permissions
from datetime import date

HTML = 'charge_date.html'

NO_VALIDATION_ERRORS = []
VALIDATION_ERRORS = {'date': ['some error message']}

CHARGE_DAY = 'some charge day'
CHARGE_MONTH = 'some charge month'
CHARGE_YEAR = 'some charge year'


class TestEditChargeCreationDate(TestCase):

    def create_app(self):
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def test_get(self):
        """should respond with a 200 and render the expected template"""
        self.mock_session.return_value.add_charge_state = LocalLandChargeItem()
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.get(url_for('modify_land_charge.get_charge_date'))

        self.status = self.assert_status(response, 200)
        self.assert_template_used(HTML)

    def test_get_with_date(self):
        """should respond with a 200 and render the expected template"""
        charge = LocalLandChargeItem()
        charge.charge_creation_date = date(2011, 1, 1)
        self.mock_session.return_value.add_charge_state = charge
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        response = self.client.get(url_for('modify_land_charge.get_charge_date'))

        self.status = self.assert_status(response, 200)
        self.assert_template_used(HTML)

    def test_get_redirects_to_error_when_state_is_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        self.mock_session.return_value.add_charge_state = None

        response = self.client.get(url_for('modify_land_charge.get_charge_date'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/error')

    @patch('maintain_frontend.view_modify_land_charge.edit_charge_date.ChargeDateValidator')
    def test_post_with_no_validation_errors(self, mock_validator):
        """should respond with a 302 and redirect to the add_land_charge_date page"""
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        charge = LocalLandChargeItem()
        charge.local_land_charge = 1
        self.mock_session.return_value.add_charge_state = charge
        self.mock_session.return_value.edited_fields = []

        mock_validator.validate.return_value.errors = NO_VALIDATION_ERRORS

        response = self.client.post(url_for('modify_land_charge.post_charge_date'), data={
            "date-day": "01",
            "date-month": "01",
            "date-year": "2001"
        })

        self.assertTrue('charge_creation_date' in self.mock_session.return_value.edited_fields)
        self.assertStatus(response, 302)
        self.assertRedirects(response, url_for('modify_land_charge.modify_land_charge', local_land_charge="LLC-1"))

    @patch('maintain_frontend.view_modify_land_charge.edit_charge_date.ChargeDateValidator')
    def test_post_with_no_validation_errors_empty_date(self, mock_validator):
        """should respond with a 302 and redirect to the add_land_charge_date page"""
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        charge = LocalLandChargeItem()
        charge.local_land_charge = 1
        charge_date = {
            'day': "01",
            'month': "12",
            'year': "2016"
        }
        charge.charge_creation_date = charge_date
        self.mock_session.return_value.add_charge_state = charge
        self.mock_session.return_value.edited_fields = []

        mock_validator.validate.return_value.errors = NO_VALIDATION_ERRORS

        response = self.client.post(url_for('modify_land_charge.post_charge_date'), data={
            "date-day": "",
            "date-month": "",
            "date-year": ""
        })

        self.assertTrue('charge_creation_date' in self.mock_session.return_value.edited_fields)
        self.assertStatus(response, 302)
        self.assertRedirects(response, url_for('modify_land_charge.modify_land_charge', local_land_charge="LLC-1"))

    @patch('maintain_frontend.view_modify_land_charge.edit_charge_date.ChargeDateValidator')
    def test_post_with_validation_errors(self, mock_validator):
        """Should respond with a 200, render the expected template, and return the expected error object."""
        self.mock_session.return_value.add_charge_state = LocalLandChargeItem()
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        mock_validator.validate.return_value.errors = VALIDATION_ERRORS

        response = self.client.post(url_for('modify_land_charge.post_charge_date'), data={
            'date-day': CHARGE_DAY,
            'date-month': CHARGE_MONTH,
            'date-year': CHARGE_YEAR
        })

        mock_validator.validate.assert_called_with(CHARGE_DAY, CHARGE_MONTH, CHARGE_YEAR)

        self.assert_status(response, 200)
        self.assert_template_used(HTML)
        self.assert_context('validation_errors', VALIDATION_ERRORS)

    def test_post_redirects_to_error_when_state_is_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        self.mock_session.return_value.add_charge_state = None

        response = self.client.post(url_for('modify_land_charge.post_charge_date'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/error')
