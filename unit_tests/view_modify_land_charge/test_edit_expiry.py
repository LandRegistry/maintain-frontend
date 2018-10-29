from maintain_frontend import main
from flask_testing import TestCase
from flask import url_for
from unit_tests.utilities import Utilities
from unittest.mock import patch
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.constants.permissions import Permissions
import datetime


class TestExpiry(TestCase):

    def create_app(self):
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def test_edit_expiry_get_error_without_state(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        self.mock_session.return_value.add_charge_state = None

        response = self.client.get(url_for('modify_land_charge.get_expiry'))
        self.assert_status(response, 302)
        self.assertRedirects(response, '/error')

    def test_edit_expiry_get(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        state = LocalLandChargeItem()
        state.expiry_date = datetime.date(2010, 10, 10)
        self.mock_session.return_value.add_charge_state = state

        response = self.client.get(url_for('modify_land_charge.get_expiry'))
        self.assert_status(response, 200)
        self.assert_template_used('expiry.html')

    def test_expiry_post_error_without_state(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        self.mock_session.return_value.add_charge_state = None
        response = self.client.post(url_for('modify_land_charge.post_expiry'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/error')

    @patch('maintain_frontend.view_modify_land_charge.edit_expiry.ExpiryValidator')
    def test_expiry_post_validation_errors(self, mock_expiry_validator):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        state = LocalLandChargeItem()
        state.geometry = "abc"

        self.mock_session.return_value.add_charge_state = state
        validation_errors = {'does_charge_expire': 'test error message'}
        mock_expiry_validator.validate.return_value.errors = validation_errors
        response = self.client.post(url_for('modify_land_charge.post_expiry'))

        self.assert_status(response, 400)
        self.assert_context('validation_errors', validation_errors)

    def test_expiry_post_charge_does_not_expire(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.local_land_charge = 1

        self.mock_session.return_value.add_charge_state = state

        response = self.client.post(url_for('modify_land_charge.post_expiry'), data={
            'does_charge_expire': 'no'
        })

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('modify_land_charge.modify_land_charge',
                                               local_land_charge="LLC-1"))

    def test_expiry_post_charge_does_expire(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        state = LocalLandChargeItem()
        state.local_land_charge = 1
        self.mock_session.return_value.add_charge_state = state

        form_data = {
            'does_charge_expire': 'yes',
            'charge_expiry_day': '10',
            'charge_expiry_month': '10',
            'charge_expiry_year': '2010'
        }

        response = self.client.post(url_for('modify_land_charge.post_expiry'), data=form_data)

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('modify_land_charge.modify_land_charge',
                                               local_land_charge="LLC-1"))
