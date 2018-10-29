from unittest import TestCase
from unittest.mock import patch, MagicMock
from flask import g
import json
import time
from maintain_frontend.dependencies.audit_api.audit_api import AuditAPIService
from maintain_frontend import main
from maintain_frontend.exceptions import ApplicationError


class TestAuditAPISerivice(TestCase):

    def setUp(self):
        self.app = main.app.test_client()

    @patch('maintain_frontend.dependencies.audit_api.audit_api.socket')
    def test_audit_event_success(self, mock_socket):
        with main.app.test_request_context():
            mock_socket.gethostbyname.return_value = "1.1.1.1"
            self.mock_request()
            g.requests.post.return_value = self.mock_response(status_code=201)
            AuditAPIService.audit_event("A thing")
            g.requests.post.assert_called()

    @patch('maintain_frontend.dependencies.audit_api.audit_api.socket')
    def test_audit_event_timestamps(self, mock_socket):
        with main.app.test_request_context():
            mock_socket.gethostbyname.return_value = "1.1.1.1"
            self.mock_request()
            g.requests.post.return_value = self.mock_response(status_code=201)
            AuditAPIService.audit_event("A thing")
            call1 = g.requests.post.call_args
            args, kwargs = call1
            call1_timestamp = json.loads(kwargs['data'])['activity_timestamp']

            time.sleep(0.1)

            AuditAPIService.audit_event("A thing")
            call2 = g.requests.post.call_args
            args, kwargs = call2
            call2_timestamp = json.loads(kwargs['data'])['activity_timestamp']

            self.assertNotEqual(call1_timestamp, call2_timestamp)

    @patch('maintain_frontend.dependencies.audit_api.audit_api.socket')
    def test_audit_event_supinfo_success(self, mock_socket):
        with main.app.test_request_context():
            mock_socket.gethostbyname.return_value = "1.1.1.1"
            self.mock_request()
            g.requests.post.return_value = self.mock_response(status_code=201)
            AuditAPIService.audit_event("A thing", supporting_info={"another": "thing"})
            g.requests.post.assert_called()

    @patch('maintain_frontend.dependencies.audit_api.audit_api.socket')
    @patch('maintain_frontend.dependencies.audit_api.audit_api.current_app')
    def test_audit_event_exception(self, mock_app, mock_socket):
        with main.app.test_request_context():
            mock_socket.gethostbyname.return_value = "1.1.1.1"
            self.mock_request()
            g.trace_id = '123'
            g.requests.post.side_effect = Exception('Test exception')

            try:
                AuditAPIService.audit_event("A thing")
            except ApplicationError as e:
                self.assertEqual(e.http_code, 500)
                return
            self.fail()

    @patch('maintain_frontend.dependencies.audit_api.audit_api.socket')
    @patch('maintain_frontend.dependencies.audit_api.audit_api.current_app')
    def test_audit_event_non201(self, mock_app, mock_socket):
        with main.app.test_request_context():
            mock_socket.gethostbyname.return_value = "1.1.1.1"
            self.mock_request()
            g.trace_id = '123'
            g.requests.post.return_value = self.mock_response(status_code=500, text="Something went wrong")

            try:
                AuditAPIService.audit_event("A thing")
            except ApplicationError as e:
                self.assertEqual(e.http_code, 500)
                return
            self.fail()

    @patch('maintain_frontend.dependencies.audit_api.audit_api.socket')
    def test_audit_event_machine_ip_with_supporting_info(self, mock_socket):
        with main.app.test_request_context():
            mock_socket.gethostbyname.return_value = "1.1.1.1"
            self.mock_request()
            g.requests.post.return_value = self.mock_response(status_code=201)
            AuditAPIService.audit_event("A thing", supporting_info={"another": "thing"})
            g.requests.post.assert_called()
            message = json.loads(g.requests.post.call_args[1]['data'])
            self.assertIn('machine_ip', message['supporting_info'])
            self.assertEqual("1.1.1.1", message['supporting_info']['machine_ip'])
            self.assertIn('another', message['supporting_info'])
            self.assertEqual("thing", message['supporting_info']['another'])

    @patch('maintain_frontend.dependencies.audit_api.audit_api.socket')
    def test_audit_event_machine_ip_without_supporting_info(self, mock_socket):
        with main.app.test_request_context():
            mock_socket.gethostbyname.return_value = "1.1.1.1"
            self.mock_request()
            g.requests.post.return_value = self.mock_response(status_code=201)
            AuditAPIService.audit_event("A thing")
            g.requests.post.assert_called()
            message = json.loads(g.requests.post.call_args[1]['data'])
            self.assertIn('machine_ip', message['supporting_info'])
            self.assertEqual("1.1.1.1", message['supporting_info']['machine_ip'])
            self.assertNotIn('another', message['supporting_info'])

    def mock_request(self):
        g.trace_id = '333'
        g.session = MagicMock()
        g.session.user.id = "USER123"
        g.requests = MagicMock()

    def mock_response(self, status_code=200, text='', json=None):
        response = MagicMock()
        response.status_code = status_code
        response.text = text
        if json:
            response.json.return_value = json
        return response
