from unittest.mock import patch, ANY
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from maintain_frontend import main
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.models import LLC1Search
from flask import url_for


class TestLLC1Result(TestCase):
    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def test_get_redirects_when_no_state(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.llc1_state = None
        self.mock_session.return_value.user.permissions = [Permissions.request_llc1]
        response = self.client.get(url_for("create_llc1.llc1_get_result"))
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for("create_llc1.create_llc1"))

    @patch('maintain_frontend.llc1.search_result.ReportAPIService')
    @patch('maintain_frontend.llc1.search_result.AuditAPIService')
    @patch("maintain_frontend.llc1.search_result.LLC1DocumentService")
    def test_get_renders_when_state_ok(self, mock_document_service, mock_audit, mock_report_api_service):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.llc1_state = LLC1Search()

        mock_document_service.return_value.generate.return_value = {
            "document_url": "http://example.com",
            "external_url": "external-url",
            "number_of_charges": 0
        }

        self.mock_session.return_value.user.permissions = [Permissions.request_llc1]

        response = self.client.get(url_for("create_llc1.llc1_get_result"))

        self.assert_status(response, 200)
        self.assert_template_used("search_result.html")
        mock_report_api_service.send_number_of_charges_per_search_data.assert_called_with({
            'date': ANY, 'channel': 'MAINTAIN', 'number_of_charges': 0, 'repeat': False
        })

    @patch('maintain_frontend.llc1.search_result.ReportAPIService')
    @patch('maintain_frontend.llc1.search_result.AuditAPIService')
    @patch("maintain_frontend.llc1.search_result.LLC1DocumentService")
    def test_get_renders_when_state_ok_with_supporting_documents(
        self, mock_document_service, mock_audit, mock_report_api_service
    ):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.llc1_state = LLC1Search()

        mock_document_service.return_value.generate.return_value = {
            "document_url": "http://example.com",
            "external_url": "external-url",
            "supporting_documents": [
                {"LLC1": "http://example.com"}
            ],
            "number_of_charges": 1
        }

        self.mock_session.return_value.user.permissions = [Permissions.request_llc1]

        response = self.client.get(url_for("create_llc1.llc1_get_result"))
        self.assert_status(response, 200)
        self.assert_template_used("search_result.html")
        mock_report_api_service.send_number_of_charges_per_search_data.assert_called_with({
            'date': ANY, 'channel': 'MAINTAIN', 'number_of_charges': 1, 'repeat': False
        })

    def test_get_without_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = []
        response = self.client.get(url_for("create_llc1.llc1_get_result"))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')
