from unittest.mock import Mock
from flask_testing import TestCase
from flask import url_for
import mock
from maintain_frontend import main
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.dependencies.session_api.session import Session
from unit_tests.utilities import Utilities


class TestSearch(TestCase):
    SEARCH_PATH = 'maintain_frontend.search.search'

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_index(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.user.permissions = [Permissions.browse_llc]
        self.mock_session.return_value.add_charge_state = 'test'
        self.mock_session.return_value.commit = Mock()

        response = self.client.get(url_for('search.index'))

        self.assert200(response)
        self.assertTrue(self.mock_session.return_value.commit.called)
        self.assertIsNone(self.mock_session.return_value.add_charge_state)

    @mock.patch("{}.SearchByText".format(SEARCH_PATH))
    @mock.patch("{}.request".format(SEARCH_PATH))
    def test_search_by_text_successful(self, mock_request, mock_search_by_text):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        mock_request.is_xhr = True
        mock_request.args.get.return_value = 'search query'
        mock_search_by_text.process.return_value = {'key': 'value'}

        self.client.get(
            url_for('search.search_by_text_endpoint', version="v1"),
            query_string='text'
        )

        self.assertTrue(mock_search_by_text.return_value.process.called)

    @mock.patch("{}.SearchByText".format(SEARCH_PATH))
    @mock.patch("{}.request".format(SEARCH_PATH))
    def test_search_by_text_no_xhr(self, mock_request, mock_search_by_text):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        mock_request.is_xhr = False
        mock_request.args.get.return_value = 'search query'
        mock_search_by_text.process.return_value = {'key': 'value'}

        response = self.client.get(
            url_for('search.search_by_text_endpoint', version="v1"),
            query_string='text'
        )

        self.assertRedirects(response, '/error')
        self.assertFalse(mock_search_by_text.process.called)

    @mock.patch("{}.SearchByArea".format(SEARCH_PATH))
    def test_search_by_area_xhr(self, mock_search_by_area):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        expected_input = '[[1, 1], [2, 2], [3, 3], [4, 4], [1, 1]]'

        mock_search_by_area.process.return_value = {}

        self.client.post(
            url_for('search.search_by_area_endpoint'),
            data=expected_input,
            headers=[('X-Requested-With', 'XMLHttpRequest')]
        )

        mock_search_by_area.return_value.process.assert_called_with(expected_input)

    @mock.patch("{}.SearchByArea".format(SEARCH_PATH))
    @mock.patch("{}.request".format(SEARCH_PATH))
    def test_search_by_area_no_xhr(self, mock_request, mock_search_by_area):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        expected_input = '[[1, 1], [2, 2], [3, 3], [4, 4], [1, 1]]'

        mock_request.is_xhr = False
        mock_request.args.get.return_value = expected_input
        mock_search_by_area.process.return_value = {}

        response = self.client.post(
            url_for('search.search_by_area_endpoint'),
            data=expected_input,
        )

        self.assertRedirects(response, '/error')
        self.assertFalse(mock_search_by_area.return_value.process.called)
