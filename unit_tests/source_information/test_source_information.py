from flask_testing import TestCase
from flask import url_for
from maintain_frontend import main
from unit_tests.utilities import Utilities
from unittest.mock import patch
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.constants.permissions import Permissions


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

    @patch('maintain_frontend.source_information.source_information.LocalAuthorityService')
    def test_get_source_information(self, mock_local_authority_service):
        self.mock_session.return_value.user.permissions = [Permissions.manage_source_information]
        self.mock_session.return_value.two_factor_authentication_passed = True
        mock_local_authority_service.return_value.get_source_information_for_organisation.return_value = []

        response = self.client.get(url_for('source_info.get_source_information'))

        self.assert200(response)
        self.assertTrue(self.mock_session.return_value.commit.called)
        self.assertIsNone(self.mock_session.return_value.source_information)

    def test_get_source_information_no_permissions(self):
        self.mock_session.return_value.user.permissions = []
        self.mock_session.return_value.two_factor_authentication_passed = True

        response = self.client.get(url_for('source_info.get_source_information'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')

    @patch('maintain_frontend.decorators.config')
    def test_get_source_information_2fa_not_passed(self, mock_config):
        self.mock_session.return_value.user.permissions = [Permissions.manage_source_information]
        mock_config.ENABLE_TWO_FACTOR_AUTHENTICATION = True
        self.mock_session.return_value.two_factor_authentication_passed = False

        response = self.client.get(url_for('source_info.get_source_information'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/check-your-email')

    @patch('maintain_frontend.source_information.source_information.LocalAuthorityService')
    @patch('maintain_frontend.decorators.config')
    def test_2fa_skipped_when_disabled(self, mock_config, mock_local_authority_service):
        self.mock_session.return_value.user.permissions = [Permissions.manage_source_information]
        self.mock_session.return_value.two_factor_authentication_passed = False
        mock_config.ENABLE_TWO_FACTOR_AUTHENTICATION = False
        mock_local_authority_service.return_value.get_source_information_for_organisation.return_value = []

        response = self.client.get(url_for('source_info.get_source_information'))

        self.assert200(response)
        self.assertTrue(self.mock_session.return_value.commit.called)
        self.assertIsNone(self.mock_session.return_value.source_information)
