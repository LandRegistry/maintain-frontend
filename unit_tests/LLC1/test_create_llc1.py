from flask_testing import TestCase
from unit_tests.utilities import Utilities
from maintain_frontend import main
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.constants.permissions import Permissions
from flask import url_for


class TestCreateLLC1(TestCase):
    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def test_create_llc1(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.request_llc1]
        response = self.client.get(url_for("create_llc1.create_llc1"))
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for("create_llc1.llc1_get_location"))
        self.mock_session.return_value.commit.assert_called()
