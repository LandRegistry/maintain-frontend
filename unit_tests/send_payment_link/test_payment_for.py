from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from flask import url_for
from unittest.mock import patch
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.dependencies.session_api.session import Session


class TestPaymentFor(TestCase):
    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_payment_for_redirects_to_new_when_state_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.send_payment_link_info = None
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        response = self.client.get(url_for('send_payment_link.get_payment_for'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('send_payment_link.send_payment_link'))

    def test_payment_for_get(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        response = self.client.get(url_for('send_payment_link.get_payment_for'))

        self.assert_status(response, 200)
        self.assert_template_used('payment_for.html')

    def test_payment_for_no_permission_redirects(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.user.permissions = []

        response = self.client.get(url_for('send_payment_link.get_payment_for'))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')

        response = self.client.get(url_for('send_payment_link.post_payment_for'))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')

    @patch('maintain_frontend.send_payment_link.payment_for.request')
    @patch('maintain_frontend.send_payment_link.payment_for.PaymentReasonValidator')
    def test_post_valid_payment_for_lon(self, mock_validator, mock_request):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        mock_request.form = {
            'payment_for': 'lon'
        }

        mock_validator.validate.return_value.errors = None

        response = self.client.post(url_for('send_payment_link.post_payment_for'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('send_payment_link.get_enter_email'))

    @patch('maintain_frontend.send_payment_link.payment_for.request')
    @patch('maintain_frontend.send_payment_link.payment_for.PaymentReasonValidator')
    def test_post_valid_payment_for_official_search(self, mock_validator, mock_request):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        mock_request.form = {
            'payment_for': 'official_search'
        }

        mock_validator.validate.return_value.errors = None

        response = self.client.post(url_for('send_payment_link.post_payment_for'))

        self.assert_status(response, 302)
        # TODO(official_search) replace this with actual page for official search payment once done
        self.assertRedirects(response, url_for('home.get'))

    @patch('maintain_frontend.send_payment_link.payment_for.request')
    @patch('maintain_frontend.send_payment_link.payment_for.PaymentReasonValidator')
    def test_post_invalid_payment_for(self, mock_validator, mock_request):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        mock_request.form = {
            'payment_for': 'something wrong'
        }

        error = {'payment_for': ['some error message']}
        mock_validator.validate.return_value.errors = error

        response = self.client.post(url_for('send_payment_link.post_payment_for'))

        self.assert_context('validation_errors', error)
        self.assert_status(response, 400)
        self.assert_template_used('payment_for.html')
