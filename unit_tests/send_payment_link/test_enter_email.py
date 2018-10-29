from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from flask import url_for
from unittest.mock import patch
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.dependencies.session_api.session import Session


class TestEnterEmail(TestCase):
    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_enter_email_redirects_to_new_when_state_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.send_payment_link_info = None
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        response = self.client.get(url_for('send_payment_link.get_enter_email'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('send_payment_link.send_payment_link'))

    def test_enter_email_get(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.send_payment_link_info.email = 'test@test.com'
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        response = self.client.get(url_for('send_payment_link.get_enter_email'))

        self.assert_status(response, 200)
        self.assert_template_used('enter_email.html')

    def test_enter_email_no_permission_redirects(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.user.permissions = []

        response = self.client.get(url_for('send_payment_link.get_enter_email'))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')

        response = self.client.get(url_for('send_payment_link.post_enter_email'))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')

    @patch('maintain_frontend.send_payment_link.enter_email.AuditAPIService')
    @patch('maintain_frontend.send_payment_link.enter_email.NotificationAPIService')
    @patch('maintain_frontend.send_payment_link.enter_email.request')
    @patch('maintain_frontend.send_payment_link.enter_email.CustomerEmailValidator')
    def test_post_valid_email(self, mock_validator, mock_request, mock_notification, mock_audit):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        mock_request.form = {
            'email': 'test@test.com'
        }

        mock_validator.validate.return_value.errors = None

        response = self.client.post(url_for('send_payment_link.post_enter_email'))

        mock_notification.send_message_notify.assert_called_once()
        mock_audit.send_message_notify.assert_called_once()
        self.assert_status(response, 200)
        self.assert_template_used('email_confirmation.html')

    @patch('maintain_frontend.send_payment_link.enter_email.AuditAPIService')
    @patch('maintain_frontend.send_payment_link.enter_email.NotificationAPIService')
    @patch('maintain_frontend.send_payment_link.enter_email.request')
    @patch('maintain_frontend.send_payment_link.enter_email.CustomerEmailValidator')
    def test_post_invalid_email(self, mock_validator, mock_request, mock_notification, mock_audit):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        mock_request.form = {
            'email': 'test@test.com'
        }

        error = {'email': ['some error message']}
        mock_validator.validate.return_value.errors = error

        response = self.client.post(url_for('send_payment_link.post_enter_email'))

        self.assert_context('validation_errors', error)
        self.assert_status(response, 400)
        self.assert_template_used('enter_email.html')
