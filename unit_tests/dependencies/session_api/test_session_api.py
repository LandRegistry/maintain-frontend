from unittest import TestCase
from maintain_frontend.main import app
from flask import g
from unittest.mock import patch, MagicMock
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.dependencies.session_api.session_service import SessionAPIService

SESSION_API_NAME = 'maintain_frontend.dependencies.session_api.session_service'
TEST_SUBSECTION = 'Test'


class TestSessionApiService(TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_get_session_state_successful(self):
        with app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = '123'
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = {"test": '123'}
            g.requests.get.return_value = response

            result = SessionAPIService.get_session_state('abc', 'def')

            self.assertIsNotNone(result)
            self.assertEqual({"test": '123'}, result)

    def test_get_session_state_none_500(self):
        with app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = '123'
            response = MagicMock()
            response.status_code = 500
            response.json.return_value = {"test": '123'}
            g.requests.get.return_value = response

            result = SessionAPIService.get_session_state('abc', 'def')

            self.assertIsNone(result)

    def test_get_session_state_none_on_exception(self):
        with app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = '123'
            response = MagicMock()
            response.status_code = 500
            response.json.return_value = {"test": '123'}
            g.requests.get.side_effect = Exception('test exception')

            result = SessionAPIService.get_session_state('abc', 'def')

            self.assertIsNone(result)

    def test_create_session_successful(self):
        with app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = '123'
            response = MagicMock()
            response.status_code = 200
            response.text = "session key"
            g.requests.post.return_value = response

            result = SessionAPIService.create_session('abc')

            self.assertIsNotNone(result)
            self.assertEqual('session key', result)

    @patch('{}.current_app'.format(SESSION_API_NAME))
    def test_create_session_non_200_response(self, mock_app):
        with app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = '123'
            response = MagicMock()
            response.status_code = 500
            response.text = "session key"
            g.requests.post.return_value = response

            try:
                SessionAPIService.create_session('abc')
            except ApplicationError as ex:
                self.assertEqual(ex.http_code, 500)
                mock_app.logger.exception.assert_called()
                mock_app.logger.exception.assert_called_with(
                    'Failed to create session. TraceID : {} - Status code:{}, message:{}'.format(
                        "123",
                        "500",
                        "session key"))
                return
            self.fail()

    @patch('{}.current_app'.format(SESSION_API_NAME))
    def test_create_session_exception_response(self, mock_app):
        with app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = '123'
            response = MagicMock()
            response.status_code = 500
            response.text = "session key"
            g.requests.post.side_effect = Exception('test exception')

            try:
                SessionAPIService.create_session('abc')
            except ApplicationError as ex:
                self.assertEqual(ex.http_code, 500)
                mock_app.logger.exception.assert_called()
                mock_app.logger.exception.assert_called_with(
                    'Failed to create session. TraceID : 123 - Exception - test exception')
                return
            self.fail()

    def test_update_session_successful(self):
        with app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = '123'
            response = MagicMock()
            response.status_code = 201
            response.text = "session key"
            g.requests.put.return_value = response

            SessionAPIService.update_session_data(
                1,
                {'data': 'some value'},
                TEST_SUBSECTION
            )

            self.assertTrue(True)

    @patch('{}.current_app'.format(SESSION_API_NAME))
    def test_update_session_failure_non_200(self, mock_app):
        with app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = '123'
            response = MagicMock()
            response.status_code = 500
            response.text = "session key"
            g.requests.put.return_value = response

            try:
                SessionAPIService.update_session_data(
                    1,
                    {'data': 'some value'},
                    TEST_SUBSECTION
                )
            except ApplicationError as ex:
                self.assertEqual(ex.http_code, 500)
                mock_app.logger.exception.assert_called()
                mock_app.logger.exception.assert_called_with(
                    'Error when updating session data for session ID 1. TraceID : 123 - Message - session key')
                return
            self.fail()

    @patch('{}.current_app'.format(SESSION_API_NAME))
    def test_update_session_failure_exception(self, mock_app):
        with app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = '123'
            response = MagicMock()
            response.status_code = 200
            response.text = "session key"
            g.requests.put.side_effect = Exception("test")

            try:
                SessionAPIService.update_session_data(
                    1,
                    {'data': 'some value'},
                    TEST_SUBSECTION
                )
            except ApplicationError as ex:
                self.assertEqual(ex.http_code, 500)
                mock_app.logger.exception.assert_called()
                mock_app.logger.exception.assert_called_with(
                    'Failed to update session. TraceID : 123 - Exception - test')
                return
            self.fail()

    def test_session_valid_successful(self):
        with app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = '123'
            response = MagicMock()
            response.status_code = 200
            g.requests.get.return_value = response

            result = SessionAPIService.session_valid("abc")

            self.assertTrue(result)

    def test_session_valid_non_200(self):
        with app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = '123'
            response = MagicMock()
            response.status_code = 500
            g.requests.get.return_value = response

            result = SessionAPIService.session_valid("abc")

            self.assertFalse(result)

    def test_session_valid_exception(self):
        with app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = '123'
            response = MagicMock()
            response.status_code = 200
            g.requests.get.side_effect = Exception('test exception')

            result = SessionAPIService.session_valid("abc")

            self.assertFalse(result)

    def test_session_expire_success(self):
        with app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = '123'
            response = MagicMock()
            response.status_code = 200
            g.requests.delete.return_value = response

            SessionAPIService.expire_session("abc")

            self.assertTrue(True)

    def test_session_expire_success_on_non_200(self):
        with app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = '123'
            response = MagicMock()
            response.status_code = 200
            g.requests.delete.return_value = response

            SessionAPIService.expire_session("abc")

            self.assertTrue(True)

    def test_session_expire_success_on_exception(self):
        with app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = '123'
            response = MagicMock()
            response.status_code = 200
            g.requests.delete.side_effect = Exception('test exception')

            SessionAPIService.expire_session("abc")

            self.assertTrue(True)
