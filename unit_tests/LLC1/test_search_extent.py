from flask_testing import TestCase
from unit_tests.utilities import Utilities
from unittest.mock import patch
from maintain_frontend import main
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.models import LLC1Search
from flask import url_for
import json


class TestLLC1Description(TestCase):
    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def test_get_redirects_when_no_state(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.llc1_state = None
        self.mock_session.return_value.user.permissions = [Permissions.request_llc1]

        response = self.client.get(url_for("create_llc1.llc1_get_extent"))
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for("create_llc1.create_llc1"))

    def test_get_renders_when_state_ok(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.llc1_state = LLC1Search()
        self.mock_session.return_value.user.permissions = [Permissions.request_llc1]

        response = self.client.get(url_for("create_llc1.llc1_get_extent"))
        self.assert_status(response, 200)
        self.assert_template_used("search_extent.html")

    def test_get_no_location_redirects_when_no_state(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.llc1_state = None
        self.mock_session.return_value.user.permissions = [Permissions.request_llc1]

        response = self.client.get(url_for("create_llc1.llc1_get_extent_no_location"))
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for("create_llc1.create_llc1"))

    def test_get_no_location_redirects_when_state_ok(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.llc1_state = LLC1Search()
        self.mock_session.return_value.user.permissions = [Permissions.request_llc1]

        response = self.client.get(url_for("create_llc1.llc1_get_extent_no_location"))
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for("create_llc1.llc1_get_extent"))

    def test_post_redirects_when_no_state(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.llc1_state = None
        self.mock_session.return_value.user.permissions = [Permissions.request_llc1]

        response = self.client.post(url_for("create_llc1.llc1_set_extent"),
                                    data={'saved-features': 'foo'})
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for("create_llc1.create_llc1"))

    def test_post_renders_error_with_no_saved_features(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.llc1_state = LLC1Search()
        self.mock_session.return_value.user.permissions = [Permissions.request_llc1]
        response = self.client.post(url_for("create_llc1.llc1_set_extent"),
                                    data={'saved-features': []})
        self.assertStatus(response, 400)
        self.assert_template_used('search_extent.html')

    @patch('maintain_frontend.llc1.search_extent.LocalAuthorityService')
    def test_post_redirects_when_extent_is_within_migrated_area(self, local_authority_service_mock):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.llc1_state = LLC1Search()
        self.mock_session.return_value.user.permissions = [Permissions.request_llc1]
        feature_collection = json.dumps({
            "type": "FeatureCollection",
            "features": [{
                "geometry": {"type": "Point", "coordinates": [1, 2]},
                "properties": None,
                "id": None
            }]
        })
        local_authority_service_mock.return_value.is_extent_within_migrated_area.return_value = True
        response = self.client.post(url_for("create_llc1.llc1_set_extent"),
                                    data={'saved-features': feature_collection})
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for("create_llc1.llc1_get_description"))

    @patch('maintain_frontend.llc1.search_extent.LocalAuthorityService')
    def test_post_redirects_when_extent_is_within_non_migrated_area(self, local_authority_service_mock):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.llc1_state = LLC1Search()
        self.mock_session.return_value.user.permissions = [Permissions.request_llc1]
        feature_collection = json.dumps({
            "type": "FeatureCollection",
            "features": [{
                "geometry": {"type": "Point", "coordinates": [1, 2]},
                "properties": None,
                "id": None
            }]
        })
        local_authority_service_mock.return_value.is_extent_within_migrated_area.return_value = False
        response = self.client.post(url_for("create_llc1.llc1_set_extent"),
                                    data={'saved-features': feature_collection})
        self.assert_status(response, 400)
        self.assert_template_used("search_extent.html")
        self.assert_context("is_valid_search_extent", False)

    def test_get_without_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = []
        response = self.client.get(url_for("create_llc1.llc1_get_extent"))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')

    def test_get_no_location_without_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = []
        response = self.client.get(url_for("create_llc1.llc1_get_extent_no_location"))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')

    def test_post_without_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = []
        response = self.client.get(url_for("create_llc1.llc1_set_extent"))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')
