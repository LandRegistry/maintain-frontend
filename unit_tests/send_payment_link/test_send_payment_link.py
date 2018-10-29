from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from flask import url_for
from maintain_frontend.dependencies.session_api.session import Session


class TestSendPaymentLink(TestCase):
    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_payment_link_redirects(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        response = self.client.get(url_for('send_payment_link.send_payment_link'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('send_payment_link.get_payment_for'))
