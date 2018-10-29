from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from flask import url_for
from maintain_frontend.dependencies.session_api.session import Session


class TestViewOfficialSearch (TestCase):

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_add_new(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        response = self.client.get(url_for('view_official_search.new'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('view_official_search.get_enter_search_ref'))
        self.mock_session.return_value.commit.assert_called()
