from maintain_frontend import main
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.dependencies.session_api.session import Session
from flask import url_for, current_app
from flask_testing import TestCase
from unittest.mock import patch
from unit_tests.utilities import Utilities
import jwt


REPORTVIEWER_PATH = 'maintain_frontend.reports.report_downloader'


class TestReportDownloader(TestCase):
    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    @patch('{}.StorageAPIService'.format(REPORTVIEWER_PATH))
    def test_download_report_success(self, mock_storage_api_service):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        mock_authority = 'City of London'
        unencoded_token = {
            'report_id': 1,
            'authority': mock_authority
        }

        self.mock_session.return_value.user.permissions = [Permissions.view_report]
        self.mock_session.return_value.user.organisation = mock_authority
        mock_storage_api_service.get_external_url.return_value = "test"

        url = '{}?token={}'.format(url_for('reports.get_expired_charges_report'), self.encode_token(unencoded_token))

        response = self.client.get(url)

        self.assert_status(response, 200)
        self.assert_template_used('expired_charges_report_download.html')

    def test_download_report_token_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        mock_authority = 'City of London'

        self.mock_session.return_value.user.permissions = [Permissions.view_report]
        self.mock_session.return_value.user.organisation = mock_authority

        url = url_for('reports.get_expired_charges_report')

        response = self.client.get(url)

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')

    def test_download_report_incorrect_fields(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        mock_authority = 'City of London'
        unencoded_token = {
            'report_id': 1,
            'auth0rity': mock_authority,
        }

        self.mock_session.return_value.user.permissions = [Permissions.view_report]
        self.mock_session.return_value.user.organisation = mock_authority

        url = '{}?token={}'.format(url_for('reports.get_expired_charges_report'), self.encode_token(unencoded_token))

        response = self.client.get(url)

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')

    def test_download_report_authority_mismatch(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        mock_authority_1 = 'City of London'
        mock_authority_2 = 'Exeter'
        unencoded_token = {
            'report_id': 1,
            'authority': mock_authority_1
        }

        self.mock_session.return_value.user.permissions = [Permissions.view_report]
        self.mock_session.return_value.user.organisation = mock_authority_2

        url = '{}?token={}'.format(url_for('reports.get_expired_charges_report'), self.encode_token(unencoded_token))

        response = self.client.get(url)

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')

    def test_download_report_incorrect_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        mock_authority = 'City of London'
        unencoded_token = {
            'report_id': 1,
            'authority': mock_authority
        }

        self.mock_session.return_value.user.permissions = [Permissions.account_management]
        self.mock_session.return_value.user.organisation = mock_authority

        url = '{}?token={}'.format(url_for('reports.get_expired_charges_report'), self.encode_token(unencoded_token))

        response = self.client.get(url)

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')

    @patch('{}.StorageAPIService'.format(REPORTVIEWER_PATH))
    def test_download_report_no_url_returned(self, mock_storage_api_service):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        mock_authority = 'City of London'
        unencoded_token = {
            'report_id': 1,
            'authority': mock_authority
        }

        self.mock_session.return_value.user.permissions = [Permissions.view_report]
        self.mock_session.return_value.user.organisation = mock_authority
        mock_storage_api_service.return_value.get_external_url.return_value = None
        url = '{}?token={}'.format(url_for('reports.get_expired_charges_report'), self.encode_token(unencoded_token))

        response = self.client.get(url)

        self.assert_status(response, 302)
        self.assertRedirects(response, '/page-not-found')

    @patch('{}.StorageAPIService'.format(REPORTVIEWER_PATH))
    def test_download_report_expired_invalid_signature(self, mock_storage_api_service):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        unencoded_token = {
            'report_id': 1,
            'authority': 'unit test'
        }

        self.mock_session.return_value.user.permissions = [Permissions.view_report]
        self.mock_session.return_value.user.organisation = 'unit test'
        mock_storage_api_service.return_value.get_external_url.return_value = "abc"
        url = '{}?token={}'.format(url_for('reports.get_expired_charges_report'),
                                   '{}123'.format(self.encode_token(unencoded_token)))

        response = self.client.get(url)

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')

    @staticmethod
    def encode_token(unencoded_token):

        return jwt.encode(unencoded_token,
                          current_app.config['EXPIRED_REPORT_KEY'],
                          algorithm='HS256').decode("utf-8")
