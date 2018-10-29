from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from flask import url_for
from unittest.mock import patch, MagicMock
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import SearchDetails


class TestEnterSearchRef(TestCase):
    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_view_search_redirects_to_new_when_state_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.search_details = None
        self.mock_session.return_value.user.is_lr.return_value = True

        response = self.client.get(url_for('view_official_search.get_enter_search_ref'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('view_official_search.new'))

    def test_view_search_get(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = SearchDetails()
        self.mock_session.search_details = state
        self.mock_session.return_value.user.is_lr.return_value = True

        response = self.client.get(url_for('view_official_search.get_enter_search_ref'))

        self.assert_status(response, 200)
        self.assert_template_used('enter_search_ref.html')

    def test_view_search_no_permission_redirects(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.user.is_lr.return_value = False

        response = self.client.get(url_for('view_official_search.get_enter_search_ref'))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')

        response = self.client.post(url_for('view_official_search.post_enter_search_ref'))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')

    @patch('maintain_frontend.view_official_search.enter_search_ref.SearchReferenceValidator')
    def test_post_with_validation_errors(self, mock_validator):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.is_lr.return_value = True

        mock_validator.validate.return_value.errors = {"error": "test-error"}

        response = self.client.post(url_for('view_official_search.post_enter_search_ref'))

        self.assert_status(response, 400)
        self.assert_template_used('enter_search_ref.html')
        self.assert_context("validation_errors", {"error": "test-error"})

    @patch('maintain_frontend.view_official_search.enter_search_ref.SearchLLCAPIService')
    @patch('maintain_frontend.view_official_search.enter_search_ref.SearchReferenceValidator')
    def test_post_with_no_validation_errors(self, mock_validator, mock_llc_api):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.is_lr.return_value = True

        mock_validator.validate.return_value.errors = []

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"search-date": "2018-10-31T12:34:56+00:00",
                                           "search-area-description": "A test search area",
                                           "document-url": "",
                                           "lapsed-date": ""}

        mock_llc_api.get_by_reference_number.return_value = mock_response

        data = {
            'search_reference': '000 001 230'
        }

        response = self.client.post(url_for('view_official_search.post_enter_search_ref'), data=data)

        mock_llc_api.get_by_reference_number.assert_called_with('1230')
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('view_official_search.get_search_results'))

    @patch('maintain_frontend.view_official_search.enter_search_ref.SearchLLCAPIService')
    @patch('maintain_frontend.view_official_search.enter_search_ref.SearchReferenceValidator')
    def test_post_with_no_results(self, mock_validator, mock_llc_api):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.is_lr.return_value = True

        mock_validator.validate.return_value.errors = []

        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_llc_api.get_by_reference_number.return_value = mock_response

        data = {
            'search_reference': '000 001 230'
        }

        response = self.client.post(url_for('view_official_search.post_enter_search_ref'), data=data)

        self.assert_status(response, 400)
        self.assert_template_used('enter_search_ref.html')

    @patch('maintain_frontend.view_official_search.enter_search_ref.SearchLLCAPIService')
    @patch('maintain_frontend.view_official_search.enter_search_ref.SearchReferenceValidator')
    def test_post_with_api_down(self, mock_validator, mock_llc_api):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.is_lr.return_value = True

        mock_validator.validate.return_value.errors = []

        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_llc_api.get_by_reference_number.return_value = mock_response

        data = {
            'search_reference': '000 001 230'
        }

        response = self.client.post(url_for('view_official_search.post_enter_search_ref'), data=data)

        self.assert_status(response, 302)
        self.assertEqual(response.location, 'http://localhost/error')

    @patch('maintain_frontend.view_official_search.enter_search_ref.SearchLLCAPIService')
    @patch('maintain_frontend.view_official_search.enter_search_ref.SearchReferenceValidator')
    def test_post_with_parent_lapsed(self, mock_validator, mock_llc_api):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.is_lr.return_value = True

        mock_validator.validate.return_value.errors = []

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"search-date": "2018-04-01T12:34:56+00:00",
                                           "search-area-description": "A test search area",
                                           "document-url": "",
                                           "lapsed-date": "2018-10-01T12:34:56+00:00",
                                           "parent-search-id": "999",
                                           "search-id": "1230"}

        mock_llc_api.get_by_reference_number.return_value = mock_response

        data = {
            'search_reference': '000 001 230'
        }

        response = self.client.post(url_for('view_official_search.post_enter_search_ref'), data=data)

        mock_llc_api.get_by_reference_number.assert_called_with('999')
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('view_official_search.get_search_results'))
