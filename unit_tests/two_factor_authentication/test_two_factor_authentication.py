from flask_testing import TestCase
from flask import url_for
from unittest.mock import patch
from maintain_frontend import main
from unit_tests.utilities import Utilities
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.two_factor_authentication.two_factor_authentication import get_current_timestamp_minutes
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


CHECK_YOUR_EMAIL_HTML_CONTENT = "We've emailed a security code to the email you use to sign into this service."


class TestSourceInformation(TestCase):
    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.'
           'two_factor_authentication_code_generator')
    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.NotificationAPIService')
    def test_two_factor_authentication_get_check_your_email_code_already_set(
        self, mock_notify_api_service, mock_code_generator
    ):
        self.mock_session.return_value.user.permissions = [
            Permissions.manage_source_information,
            Permissions.account_management
        ]
        self.mock_session.return_value.two_factor_authentication_code = 12345

        response = self.client.get(url_for('two_factor_authentication.get_check_your_email'))

        self.assertFalse(self.mock_session.return_value.commit_2fa_state.called)
        self.assertFalse(mock_notify_api_service.send_message_notify.called)
        self.assertFalse(mock_code_generator.generate_code.called)
        self.assertTemplateUsed('check_your_email.html')
        self.assert200(response)

    @patch('maintain_frontend.decorators.config')
    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.config')
    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.AuditAPIService')
    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.'
           'two_factor_authentication_code_generator')
    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.NotificationAPIService')
    def test_two_factor_authentication_get_check_your_email_code_not_set_both_permissions(
        self, mock_notify_api_service, mock_code_generator, mock_audit_api_service, mock_decorator_config,
        mock_2fa_route_config
    ):
        self.mock_session.return_value.user.permissions = [
            Permissions.manage_source_information,
            Permissions.account_management
        ]
        self.mock_session.return_value.two_factor_authentication_code = None
        mock_decorator_config.ENABLE_TWO_FACTOR_AUTHENTICATION = True
        mock_2fa_route_config.ENABLE_TWO_FACTOR_AUTHENTICATION = True

        response = self.client.get(url_for('two_factor_authentication.get_check_your_email'))

        mock_audit_api_service.audit_event.assert_called_with('2FA code sent to user')
        self.assertTrue(self.mock_session.return_value.commit_2fa_state.called)
        self.assertEqual(self.mock_session.return_value.two_factor_authentication_invalid_attempts, 0)
        self.assertTrue(mock_notify_api_service.send_message_notify.called)
        self.assertTrue(mock_code_generator.generate_code.called)
        self.assertIn(CHECK_YOUR_EMAIL_HTML_CONTENT, response.data.decode())
        self.assertTemplateUsed('check_your_email.html')
        self.assert200(response)

    @patch('maintain_frontend.decorators.config')
    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.config')
    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.AuditAPIService')
    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.'
           'two_factor_authentication_code_generator')
    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.NotificationAPIService')
    def test_two_factor_authentication_get_check_your_email_code_not_set_account_management_only(
        self, mock_notify_api_service, mock_code_generator, mock_audit_api_service, mock_decorator_config,
        mock_2fa_route_config
    ):
        self.mock_session.return_value.user.permissions = [
            Permissions.account_management
        ]
        self.mock_session.return_value.two_factor_authentication_code = None
        mock_decorator_config.ENABLE_TWO_FACTOR_AUTHENTICATION = True
        mock_2fa_route_config.ENABLE_TWO_FACTOR_AUTHENTICATION = True

        response = self.client.get(url_for('two_factor_authentication.get_check_your_email'))

        mock_audit_api_service.audit_event.assert_called_with('2FA code sent to user')
        self.assertTrue(self.mock_session.return_value.commit_2fa_state.called)
        self.assertEqual(self.mock_session.return_value.two_factor_authentication_invalid_attempts, 0)
        self.assertTrue(mock_notify_api_service.send_message_notify.called)
        self.assertTrue(mock_code_generator.generate_code.called)
        self.assertTemplateUsed('check_your_email.html')
        self.assert200(response)

    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.datetime')
    def test_get_current_time_minutes_returns_time_in_minutes(self, mock_datetime):
        mock_time_seconds = 600.60
        expected_time_minutes = mock_time_seconds / 60
        mock_datetime.now.return_value.timestamp.return_value = mock_time_seconds
        returned_time = get_current_timestamp_minutes()
        self.assertEqual(returned_time, expected_time_minutes)

    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.AuditAPIService')
    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.TwoFactorAuthenticationValidator')
    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.datetime')
    def test_two_factor_authentication_post_check_your_email_success(
        self, mock_datetime, mock_validator, mock_audit_api_service
    ):
        self.mock_session.return_value.user.permissions = [
            Permissions.manage_source_information,
            Permissions.account_management
        ]
        self.mock_session.return_value.two_factor_authentication_invalid_attempts = None
        self.mock_session.return_value.two_factor_authentication_code = 12345
        self.mock_session.return_value.two_factor_authentication_redirect_url = 'redirect-url'
        self.mock_session.return_value.\
            two_factor_authentication_generation_time = 15  # 15 minutes since epoch
        mock_datetime.now.return_value.\
            timestamp.return_value = 1200                   # 20 minutes since epoch
        mock_validator.validate.return_value = ValidationErrorBuilder()

        response = self.client.post(
            url_for('two_factor_authentication.post_check_your_email'),
            data={'code': '12345'}
        )

        mock_audit_api_service.audit_event.assert_called_with('User successfully passed 2FA')
        self.assertTrue(self.mock_session.return_value.two_factor_authentication_passed)
        self.assertIsNone(self.mock_session.return_value.two_factor_authentication_invalid_attempts)
        self.assertTrue(self.mock_session.return_value.commit_2fa_state.called)
        self.assertRedirects(response, 'redirect-url')

    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.AuditAPIService')
    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.TwoFactorAuthenticationValidator')
    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.datetime')
    def test_two_factor_authentication_post_check_your_email_validation_errors(
        self, mock_datetime, mock_validator, mock_audit_api_service
    ):
        self.mock_session.return_value.user.permissions = [
            Permissions.manage_source_information,
            Permissions.account_management
        ]
        self.mock_session.return_value.two_factor_authentication_invalid_attempts = None
        self.mock_session.return_value.two_factor_authentication_code = 12345
        self.mock_session.return_value.two_factor_authentication_redirect_url = 'redirect-url'
        self.mock_session.return_value.\
            two_factor_authentication_generation_time = 15  # 15 minutes since epoch
        mock_datetime.now.return_value.\
            timestamp.return_value = 1200                   # 20 minutes since epoch
        errors = ValidationErrorBuilder()
        errors.errors['code'] = ['Invalid security code']
        mock_validator.validate.return_value = errors

        response = self.client.post(
            url_for('two_factor_authentication.post_check_your_email'),
            data={'code': '123'}
        )

        mock_audit_api_service.audit_event.assert_called_with('Invalid entry of 2FA code')
        self.assertEqual(self.mock_session.return_value.two_factor_authentication_invalid_attempts, 1)
        self.assertTrue(self.mock_session.return_value.commit_2fa_state.called)
        self.assertTemplateUsed('check_your_email.html')
        self.assertStatus(response, 400)

    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.AuditAPIService')
    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.TwoFactorAuthenticationValidator')
    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.datetime')
    def test_two_factor_authentication_post_check_your_email_validation_errors_invalid_attempts_increases(
        self, mock_datetime, mock_validator, mock_audit_api_service
    ):
        self.mock_session.return_value.user.permissions = [
            Permissions.manage_source_information,
            Permissions.account_management
        ]
        self.mock_session.return_value.two_factor_authentication_invalid_attempts = 1
        self.mock_session.return_value.two_factor_authentication_code = 12345
        self.mock_session.return_value.two_factor_authentication_redirect_url = 'redirect-url'
        self.mock_session.return_value.\
            two_factor_authentication_generation_time = 15  # 15 minutes since epoch
        mock_datetime.now.return_value.\
            timestamp.return_value = 1200                   # 20 minutes since epoch
        errors = ValidationErrorBuilder()
        errors.errors['code'] = ['Invalid security code']
        mock_validator.validate.return_value = errors

        self.client.post(
            url_for('two_factor_authentication.post_check_your_email'),
            data={'code': '12345'}
        )

        mock_audit_api_service.audit_event.assert_called_with('Invalid entry of 2FA code')
        self.assertEqual(self.mock_session.return_value.two_factor_authentication_invalid_attempts, 2)

    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.AuditAPIService')
    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.TwoFactorAuthenticationValidator')
    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.datetime')
    def test_two_factor_authentication_post_check_your_email_validation_errors_logout_redirect(
        self, mock_datetime, mock_validator, mock_audit_api_service
    ):
        self.mock_session.return_value.user.permissions = [
            Permissions.manage_source_information,
            Permissions.account_management
        ]
        self.mock_session.return_value.two_factor_authentication_invalid_attempts = 2
        self.mock_session.return_value.two_factor_authentication_code = 12345
        self.mock_session.return_value.two_factor_authentication_redirect_url = 'redirect-url'
        self.mock_session.return_value.\
            two_factor_authentication_generation_time = 15  # 15 minutes since epoch
        mock_datetime.now.return_value.\
            timestamp.return_value = 1200                   # 20 minutes since epoch
        errors = ValidationErrorBuilder()
        errors.errors['code'] = ['Invalid security code']
        mock_validator.validate.return_value = errors

        response = self.client.post(
            url_for('two_factor_authentication.post_check_your_email'),
            data={'code': '123'}
        )

        mock_audit_api_service.audit_event.assert_called_with('2FA code attempt limits exceeded')
        self.assertRedirects(response, 'logout')

    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.AuditAPIService')
    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.TwoFactorAuthenticationValidator')
    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.datetime')
    def test_two_factor_authentication_post_check_your_email_incorrect_code(
        self, mock_datetime, mock_validator, mock_audit_api_service
    ):
        self.mock_session.return_value.user.permissions = [
            Permissions.manage_source_information,
            Permissions.account_management
        ]
        self.mock_session.return_value.two_factor_authentication_invalid_attempts = None
        self.mock_session.return_value.two_factor_authentication_code = 12345
        self.mock_session.return_value.two_factor_authentication_redirect_url = 'redirect-url'
        self.mock_session.return_value.\
            two_factor_authentication_generation_time = 15  # 15 minutes since epoch
        mock_datetime.now.return_value.\
            timestamp.return_value = 1200                   # 20 minutes since epoch
        mock_validator.validate.return_value = ValidationErrorBuilder()
        invalid_code_error = ['invalid code error']
        errors = ValidationErrorBuilder()
        errors.errors['code'] = invalid_code_error
        mock_validator.generate_invalid_code_error_message.return_value = errors

        response = self.client.post(
            url_for('two_factor_authentication.post_check_your_email'),
            data={'code': '123'}
        )

        mock_audit_api_service.audit_event.assert_called_with('Invalid entry of 2FA code')
        self.assertTrue(mock_validator.generate_invalid_code_error_message.called)
        self.assertEqual(self.mock_session.return_value.two_factor_authentication_invalid_attempts, 1)
        self.assertTrue(self.mock_session.return_value.commit_2fa_state.called)
        self.assert_context('validation_errors', errors.errors)
        self.assertTemplateUsed('check_your_email.html')
        self.assertStatus(response, 400)

    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.AuditAPIService')
    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.TwoFactorAuthenticationValidator')
    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.datetime')
    def test_two_factor_authentication_post_check_your_email_code_expired(
        self, mock_datetime, mock_validator, mock_audit_api_service
    ):
        self.mock_session.return_value.user.permissions = [
            Permissions.manage_source_information,
            Permissions.account_management
        ]
        self.mock_session.return_value.two_factor_authentication_invalid_attempts = None
        self.mock_session.return_value.two_factor_authentication_code = 12345
        self.mock_session.return_value.two_factor_authentication_redirect_url = 'redirect-url'
        self.mock_session.return_value.\
            two_factor_authentication_generation_time = 5  # 5 minutes since epoch
        mock_datetime.now.return_value.\
            timestamp.return_value = 1200                  # 20 minutes since epoch
        mock_validator.validate.return_value = ValidationErrorBuilder()
        invalid_code_error = ['invalid code error']
        errors = ValidationErrorBuilder()
        errors.errors['code'] = invalid_code_error
        mock_validator.generate_invalid_code_error_message.return_value = errors

        response = self.client.post(
            url_for('two_factor_authentication.post_check_your_email'),
            data={'code': '12345'}
        )

        mock_audit_api_service.audit_event.assert_called_with('Invalid entry of 2FA code')
        self.assertTrue(mock_validator.generate_invalid_code_error_message.called)
        self.assertEqual(self.mock_session.return_value.two_factor_authentication_invalid_attempts, 1)
        self.assertTrue(self.mock_session.return_value.commit_2fa_state.called)
        self.assert_context('validation_errors', errors.errors)
        self.assertTemplateUsed('check_your_email.html')
        self.assertStatus(response, 400)

    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.AuditAPIService')
    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.TwoFactorAuthenticationValidator')
    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.datetime')
    def test_two_factor_authentication_post_check_your_email_incorrect_code_invalid_attempts_increases(
        self, mock_datetime, mock_validator, mock_audit_api_service
    ):
        self.mock_session.return_value.user.permissions = [
            Permissions.manage_source_information,
            Permissions.account_management
        ]
        self.mock_session.return_value.two_factor_authentication_invalid_attempts = 1
        self.mock_session.return_value.two_factor_authentication_code = 12345
        self.mock_session.return_value.two_factor_authentication_redirect_url = 'redirect-url'
        self.mock_session.return_value.\
            two_factor_authentication_generation_time = 15  # 15 minutes since epoch
        mock_datetime.now.return_value.\
            timestamp.return_value = 1200                   # 20 minutes since epoch
        mock_validator.validate.return_value = ValidationErrorBuilder()
        mock_validator.generate_invalid_code_error_message.return_value = ValidationErrorBuilder()

        self.client.post(
            url_for('two_factor_authentication.post_check_your_email'),
            data={'code': '123'}
        )

        mock_audit_api_service.audit_event.assert_called_with('Invalid entry of 2FA code')
        self.assertEqual(self.mock_session.return_value.two_factor_authentication_invalid_attempts, 2)

    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.AuditAPIService')
    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.TwoFactorAuthenticationValidator')
    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.datetime')
    def test_two_factor_authentication_post_check_your_email_incorrect_code_logout_redirect(
        self, mock_datetime, mock_validator, mock_audit_api_service
    ):
        self.mock_session.return_value.user.permissions = [
            Permissions.manage_source_information,
            Permissions.account_management
        ]
        self.mock_session.return_value.two_factor_authentication_invalid_attempts = 2
        self.mock_session.return_value.two_factor_authentication_code = 12345
        self.mock_session.return_value.two_factor_authentication_redirect_url = 'redirect-url'
        self.mock_session.return_value.\
            two_factor_authentication_generation_time = 15  # 15 minutes since epoch
        mock_datetime.now.return_value.\
            timestamp.return_value = 1200                   # 20 minutes since epoch
        mock_validator.validate.return_value = ValidationErrorBuilder()

        response = self.client.post(
            url_for('two_factor_authentication.post_check_your_email'),
            data={'code': '123'}
        )

        mock_audit_api_service.audit_event.assert_called_with('2FA code attempt limits exceeded')
        self.assertRedirects(response, 'logout')

    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.AuditAPIService')
    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.TwoFactorAuthenticationValidator')
    @patch('maintain_frontend.two_factor_authentication.two_factor_authentication.datetime')
    def test_two_factor_authentication_post_check_your_email_missing_session_field(
        self, mock_datetime, mock_validator, mock_audit_api_service
    ):
        self.mock_session.return_value.user.permissions = [
            Permissions.manage_source_information,
            Permissions.account_management
        ]
        self.mock_session.return_value.two_factor_authentication_invalid_attempts = 2
        self.mock_session.return_value.two_factor_authentication_code = 123
        self.mock_session.return_value.two_factor_authentication_redirect_url = 'redirect-url'
        self.mock_session.return_value.\
            two_factor_authentication_generation_time = None
        mock_datetime.now.return_value.\
            timestamp.return_value = 1200
        mock_validator.validate.return_value = ValidationErrorBuilder()

        response = self.client.post(
            url_for('two_factor_authentication.post_check_your_email'),
            data={'code': '12345'}
        )

        self.assertRedirects(response, url_for('two_factor_authentication.get_check_your_email'))

    def test_two_factor_authentication_get_send_the_code_again(self):
        self.mock_session.return_value.user.permissions = [
            Permissions.manage_source_information,
            Permissions.account_management
        ]

        self.client.get(url_for('two_factor_authentication.get_send_the_code_again'))

        self.assertTemplateUsed('send_the_code_again.html')

    def test_two_factor_authentication_post_send_the_code_again(self):
        self.mock_session.return_value.user.permissions = [
            Permissions.manage_source_information,
            Permissions.account_management
        ]
        self.mock_session.return_value.two_factor_authentication_code = 12345

        response = self.client.post(url_for('two_factor_authentication.post_send_the_code_again'))

        self.assertIsNone(self.mock_session.return_value.two_factor_authentication_code)
        self.assertTrue(self.mock_session.return_value.commit_2fa_state.called)
        self.assertRedirects(response, url_for('two_factor_authentication.get_check_your_email'))
