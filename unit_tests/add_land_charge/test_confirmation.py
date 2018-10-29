from maintain_frontend import main
from flask import url_for
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.dependencies.session_api.last_created_charge import LastCreatedCharge
from maintain_frontend.constants.permissions import Permissions


class TestConfirmation(TestCase):

    def create_app(self):
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def test_confirmation_redirects_to_new_when_state_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.last_created_charge = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_confirmation'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    def test_confirmation_renders(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        lcc = LastCreatedCharge()
        lcc.entry_number = 1
        lcc.charge_id = 123456789
        lcc.registration_date = "01/01/2000"

        self.mock_session.return_value.last_created_charge = lcc
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_confirmation'))

        self.assert_status(response, 200)
        self.assert_template_used('confirmation.html')
        self.assertIn('123456789', response.data.decode())

    def test_get_no_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = []

        response = self.client.get(url_for('add_land_charge.get_confirmation'))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')
