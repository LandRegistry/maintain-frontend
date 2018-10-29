from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from flask import url_for
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.dependencies.session_api.last_created_charge import LastCreatedCharge


class TestLONConfirmation(TestCase):

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_confirmation_renders(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        lcc = LastCreatedCharge()
        lcc.entry_number = 1
        lcc.charge_id = 123456789
        lcc.registration_date = "01/01/2000"

        self.mock_session.return_value.last_created_charge = lcc
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        response = self.client.get(url_for('add_lon.get_confirmation'))

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
