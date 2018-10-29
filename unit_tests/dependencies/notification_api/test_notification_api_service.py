from unittest import TestCase
from unittest.mock import MagicMock
from flask import g
from unit_tests.utilities import Utilities
from json import dumps
from maintain_frontend import main
from maintain_frontend.dependencies.notification_api.notification_api_service import NotificationAPIService
from maintain_frontend.exceptions import ApplicationError


test_email_address = 'test@example.com'
test_template_id = 123
test_personalisation = {'code': 12345}


class TestNotificationAPIService(TestCase):
    def setUp(self):
        self.app = main.app.test_client()
        Utilities.mock_session_cookie_unittest(self)

    def test_send_message_notify_success(self):
        with main.app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = '333'
            response = MagicMock()
            response.status_code = 201
            g.requests.post.return_value = response

            NotificationAPIService.send_message_notify(test_email_address, test_template_id, test_personalisation)

            args_tuple, kwargs = g.requests.post.call_args
            url_called, = args_tuple
            self.assertIn('notifications', url_called)
            g.requests.post.assert_called_with(
                url_called,
                headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
                data=dumps({
                    "email_address": test_email_address,
                    "template_id": test_template_id,
                    "personalisation": test_personalisation,
                    "reference": None
                })
            )

    def test_send_message_notify_success_exception_thrown(self):
        with main.app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = '333'
            response = MagicMock()
            response.status_code = 500
            g.requests.post.return_value = response

            try:
                NotificationAPIService.send_message_notify(test_email_address, test_template_id, test_personalisation)
                self.fail('ApplicationError not thrown')
            except ApplicationError:
                pass
