from flask_testing import TestCase
from unittest.mock import patch
from unit_tests.utilities import Utilities
from maintain_frontend.decorators import requires_two_factor_authentication
from maintain_frontend import main


@requires_two_factor_authentication()
def redirect_test_route():
    return 'route body'


class TestDecorators(TestCase):
    def create_app(self):
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    @patch('maintain_frontend.decorators.g')
    @patch('maintain_frontend.decorators.request')
    @patch('maintain_frontend.decorators.redirect')
    @patch('maintain_frontend.decorators.config')
    def test_two_factor_authentication_redirects(
        self, mock_config, mock_redirect, mock_request, mock_g
    ):
        mock_config.ENABLE_TWO_FACTOR_AUTHENTICATION = True
        mock_g.session.two_factor_authentication_passed = False
        mock_request.path = 'test-path'

        redirect_test_route()

        self.assertEqual(mock_g.session.two_factor_authentication_redirect_url, 'test-path')
        self.assertEqual(len(mock_g.session.commit_2fa_state.mock_calls), 1)
        mock_redirect.assert_called_with('/check-your-email')

    @patch('maintain_frontend.decorators.g')
    @patch('maintain_frontend.decorators.request')
    @patch('maintain_frontend.decorators.redirect')
    @patch('maintain_frontend.decorators.config')
    def test_two_factor_authentication_passes_if_disabled(
        self, mock_config, mock_redirect, mock_request, mock_g
    ):
        mock_config.ENABLE_TWO_FACTOR_AUTHENTICATION = False
        mock_g.session.two_factor_authentication_passed = False

        response = redirect_test_route()

        self.assertEqual(response, 'route body')
        self.assertEqual(len(mock_redirect.mock_calls), 0)

    @patch('maintain_frontend.decorators.g')
    @patch('maintain_frontend.decorators.request')
    @patch('maintain_frontend.decorators.redirect')
    @patch('maintain_frontend.decorators.config')
    def test_two_factor_authentication_passes_subsequent_checks(
        self, mock_config, mock_redirect, mock_request, mock_g
    ):
        mock_config.ENABLE_TWO_FACTOR_AUTHENTICATION = True
        mock_g.session.two_factor_authentication_passed = True

        response = redirect_test_route()

        self.assertEqual(response, 'route body')
        self.assertEqual(len(mock_redirect.mock_calls), 0)
