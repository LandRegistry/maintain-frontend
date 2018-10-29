from flask_testing import TestCase
from flask import g
from maintain_frontend import main
from unittest.mock import patch
from maintain_frontend.dependencies.session_api.session import Session


class TestApp(TestCase):

    def create_app(self):
        main.app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
        return main.app

    @patch('maintain_frontend.app.Session')
    def test_trace_id_being_set_from_header(self, mock_session):
        with main.app.app_context():
            mock_session.return_value.valid.return_value = True
            mock_session.session_cookie_name = Session.session_cookie_name
            self.client.set_cookie('localhost', Session.session_cookie_name,
                                   'cookie_value')
            response = self.client.get('/', headers={'X-Trace-ID': '123'})
            self.assert200(response)
            self.assertIsNotNone(g.trace_id)
            self.assertEqual(g.trace_id, '123')

    @patch('maintain_frontend.app.Session')
    def test_trace_id_being_generated(self, mock_session):
        with main.app.app_context():
            mock_session.return_value.valid.return_value = True
            mock_session.session_cookie_name = Session.session_cookie_name
            self.client.set_cookie('localhost', Session.session_cookie_name,
                                   'cookie_value')
            response = self.client.get('/')
            self.assert200(response)
            self.assertIsNotNone(g.trace_id)
            self.assertEqual(len(g.trace_id), 32)

    def test_if_session_key_none_redirected_to_login(self):
        with main.app.app_context():
            response = self.client.get('/')
            self.assertStatus(response, status_code=302)
            self.assert_redirects(response, '/sign-in')
            cookies = response.headers.getlist('Set-Cookie')
            self.assertIsNotNone(cookies)
            self.assertIn('Location=/', cookies[0].replace('"', ''))

    @patch('maintain_frontend.app.Session')
    def test_if_session_invalid_one_redirected_to_logout(self, mock_session):
        with main.app.app_context():
            mock_session.return_value.valid.return_value = False
            mock_session.session_cookie_name = Session.session_cookie_name
            self.client.set_cookie('localhost', Session.session_cookie_name,
                                   'cookie_value')
            response = self.client.get('/')
            self.assertStatus(response, status_code=302)
            self.assert_redirects(response, '/logout')
            cookies = response.headers.getlist('Set-Cookie')
            self.assertIsNotNone(cookies)
            self.assertIn('Location=/', cookies[0].replace('"', ''))
