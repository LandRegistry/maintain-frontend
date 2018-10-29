from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from flask import url_for
from unittest.mock import patch
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import SearchDetails
from datetime import datetime


class TestViewResults(TestCase):
    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_view_results_redirects_to_new_when_state_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.search_details = None
        self.mock_session.return_value.user.is_lr.return_value = True

        response = self.client.get(url_for('view_official_search.get_search_results'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('view_official_search.new'))

    def test_view_results_no_permission_redirects(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.user.is_lr.return_value = False

        response = self.client.get(url_for('view_official_search.get_search_results'))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')

        response = self.client.post(url_for('view_official_search.post_enter_search_ref'))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')

    def test_view_results_lapsed(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = SearchDetails()
        state.search_lapsed = True
        state.parent_lapsed = False
        state.search_reference = "1230"
        state.search_date = datetime.strptime("2018-10-31T12:34:56+00:00", "%Y-%m-%dT%H:%M:%S+00:00")
        self.mock_session.return_value.search_details = state
        self.mock_session.return_value.user.is_lr.return_value = True

        response = self.client.get(url_for('view_official_search.get_search_results'))

        self.assert_status(response, 200)
        self.assert_template_used('search_lapsed.html')

    @patch('maintain_frontend.view_official_search.search_results.StorageAPIService')
    def test_view_results_not_lapsed(self, mock_storage):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.is_lr.return_value = True

        mock_storage.get_external_url_for_document_url.return_value = "Test URL"

        state = SearchDetails()
        state.area_description = "test area"
        state.search_reference = "1230"
        self.mock_session.return_value.search_details = state

        response = self.client.get(url_for('view_official_search.get_search_results'))

        self.assert_status(response, 200)
        self.assert_template_used('download_search.html')
