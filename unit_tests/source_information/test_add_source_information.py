from flask_testing import TestCase
from flask import url_for
from maintain_frontend import main
from unit_tests.utilities import Utilities
from unittest.mock import patch
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.constants.permissions import Permissions


class TestAddSourceInformation(TestCase):
    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

    def test_get_add_source_information(self):
        self.mock_session.return_value.user.permissions = [Permissions.manage_source_information]
        response = self.client.get(url_for('source_info.get_add_source_information'))

        self.assert200(response)

    def test_get_add_source_information_no_permissions(self):
        self.mock_session.return_value.user.permissions = []

        response = self.client.get(url_for('source_info.get_add_source_information'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')

    def test_post_add_source_information(self):
        self.mock_session.return_value.user.permissions = [Permissions.manage_source_information]
        response = self.client.post(url_for('source_info.post_add_source_information'),
                                    data={'source-information': 'Test Source'})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('source_info.get_add_source_information_confirm'))

        self.assertTrue(self.mock_session.return_value.commit.called)
        self.assertEqual(self.mock_session.return_value.source_information, "Test Source")

    def test_post_add_source_information_no_permissions(self):
        self.mock_session.return_value.user.permissions = []

        response = self.client.post(url_for('source_info.post_add_source_information'),
                                    data={'source-information': 'Test Source'})

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')

    def test_post_add_source_information_empty(self):
        self.mock_session.return_value.user.permissions = [Permissions.manage_source_information]

        response = self.client.post(url_for('source_info.post_add_source_information'),
                                    data={"source-information": ""})

        self.assert_status(response, 400)
        self.assertIn("There are errors on this page", response.data.decode())

    def test_post_add_source_information_too_large(self):
        self.mock_session.return_value.user.permissions = [Permissions.manage_source_information]

        response = self.client.post(url_for('source_info.post_add_source_information'),
                                    data={'source-information': 'a' * 501})

        self.assert_status(response, 400)
        self.assertIn("There are errors on this page", response.data.decode())

    def test_get_add_source_information_confirm(self):
        self.mock_session.return_value.user.permissions = [Permissions.manage_source_information]
        self.mock_session.return_value.source_information = "Source information"
        response = self.client.get(url_for('source_info.get_add_source_information_confirm'))

        self.assert_status(response, 200)

    def test_get_add_source_information_confirm_no_permissions(self):
        self.mock_session.return_value.user.permissions = []
        self.mock_session.return_value.source_information = "Source information"
        response = self.client.get(url_for('source_info.get_add_source_information_confirm'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')

    def test_get_add_source_information_confirm_no_information(self):
        self.mock_session.return_value.user.permissions = [Permissions.manage_source_information]
        self.mock_session.return_value.source_information = None
        response = self.client.get(url_for('source_info.get_add_source_information_confirm'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('source_info.get_add_source_information'))

    @patch('maintain_frontend.source_information.add_source_information.LocalAuthorityService')
    @patch('maintain_frontend.source_information.add_source_information.request')
    def test_post_add_source_information_confirm(self, mock_request, mock_local_authority_service):
        self.mock_session.return_value.user.permissions = [Permissions.manage_source_information]
        self.mock_session.return_value.source_information = "Source information"
        self.mock_session.return_value.user.organisation = "Test Organisation"
        self.mock_session.return_value.submit_token = "previous-token"

        mock_request.form = {"csrf_token": "new-token"}

        response = self.client.post(url_for('source_info.post_add_source_information_confirm'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('source_info.get_add_source_information_success'))

        self.assertTrue(self.mock_session.return_value.commit.called)
        self.assertEqual(self.mock_session.return_value.submit_token, "new-token")
        mock_local_authority_service.return_value.add_source_information_for_organisation\
            .assert_called_with("Source information", "Test Organisation")

    def test_post_add_source_information_confirm_no_permissions(self):
        self.mock_session.return_value.user.permissions = []

        response = self.client.post(url_for('source_info.post_add_source_information_confirm'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')

    def test_get_add_source_information_success(self):
        self.mock_session.return_value.user.permissions = [Permissions.manage_source_information]
        self.mock_session.return_value.source_information = "Source information"
        response = self.client.get(url_for('source_info.get_add_source_information_success'))

        self.assert_status(response, 200)
        self.assertTrue(self.mock_session.return_value.commit.called)
        self.assertIsNone(self.mock_session.return_value.source_information)

    def test_get_add_source_information_success_no_permissions(self):
        self.mock_session.return_value.user.permissions = []
        response = self.client.get(url_for('source_info.get_add_source_information_success'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')
