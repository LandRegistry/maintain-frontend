from flask_testing import TestCase
from unit_tests.utilities import Utilities
from maintain_frontend import main
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.models import LLC1Search
from maintain_frontend.llc1.search_location import search_for_location
from unittest.mock import patch, MagicMock
from flask import url_for, g
from maintain_frontend.app import app


class TestLLC1Location(TestCase):
    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_get_redirects_when_no_state(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.llc1_state = None
        self.mock_session.return_value.user.permissions = [Permissions.request_llc1]

        response = self.client.get(url_for("create_llc1.llc1_get_location"))
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for("create_llc1.create_llc1"))

    def test_get_renders_when_state_ok(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.llc1_state = LLC1Search()
        self.mock_session.return_value.user.permissions = [Permissions.request_llc1]

        response = self.client.get(url_for("create_llc1.llc1_get_location"))
        self.assert_status(response, 200)
        self.assert_template_used("search_location.html")

    def test_post_redirects_when_no_state(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.llc1_state = None
        self.mock_session.return_value.user.permissions = [Permissions.request_llc1]

        response = self.client.post(url_for("create_llc1.llc1_post_location"),
                                    data={'location': 'foo'})
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for("create_llc1.create_llc1"))

    def test_post_renders_error_when_no_location(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.llc1_state = LLC1Search()
        self.mock_session.return_value.user.permissions = [Permissions.request_llc1]
        response = self.client.post(url_for("create_llc1.llc1_post_location"),
                                    data={'location': ''})
        self.assertStatus(response, 400)
        self.assert_template_used('search_location.html')

    @patch("maintain_frontend.llc1.search_location.search_for_location")
    def test_post_renders_error_when_address_invalid(self, search):
        search.return_value = None
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.llc1_state = LLC1Search()
        self.mock_session.return_value.user.permissions = [Permissions.request_llc1]
        response = self.client.post(url_for("create_llc1.llc1_post_location"),
                                    data={'location': 'SJHFAkD'})
        self.assertStatus(response, 400)
        self.assert_template_used('search_location.html')

    @patch("maintain_frontend.llc1.search_location.search_for_location")
    def test_post_redirects_when_location_valid(self, search):
        search.return_value = {
            "test": "object that isn't None"
        }
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.llc1_state = LLC1Search()
        self.mock_session.return_value.user.permissions = [Permissions.request_llc1]
        response = self.client.post(url_for("create_llc1.llc1_post_location"),
                                    data={'location': 'Exeter'})
        self.assertStatus(response, 302)
        self.assertRedirects(response, url_for("create_llc1.llc1_get_extent"))

    def test_get_without_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = []
        response = self.client.get(url_for("create_llc1.llc1_post_location"))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')

    def test_post_without_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = []
        response = self.client.get(url_for("create_llc1.llc1_post_location"))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')

    @patch("maintain_frontend.llc1.search_location.AddressesService")
    def test_search_for_postcode(self, service):
        with app.test_request_context():
            g.session = MagicMock()
            g.trace_id = 'foo'
            address_service = MagicMock()
            response_object = MagicMock()
            response_object.json.return_value = [{
                "geometry": {
                    "type": "Point",
                    "coordinates": [1, 2]
                }
            }]
            address_service.get_by.return_value = response_object
            service.return_value = address_service
            result = search_for_location("EX4 4AX")
            address_service.get_by.assert_called_with('postcode', "EX4 4AX")
            self.assertEqual(result['location'], 'EX4 4AX')

    @patch("maintain_frontend.llc1.search_location.AddressesService")
    def test_search_for_uprn(self, service):
        with app.test_request_context():
            g.session = MagicMock()
            g.trace_id = 'foo'
            address_service = MagicMock()
            response_object = MagicMock()
            response_object.json.return_value = [{
                "geometry": {
                    "type": "Point",
                    "coordinates": [1, 2]
                }
            }]
            address_service.get_by.return_value = response_object
            service.return_value = address_service
            result = search_for_location("123456789186")
            address_service.get_by.assert_called_with('uprn', "123456789186")
            self.assertEqual(result['location'], '123456789186')

    @patch("maintain_frontend.llc1.search_location.AddressesService")
    def test_search_free_text(self, service):
        with app.test_request_context():
            g.session = MagicMock()
            g.trace_id = 'foo'
            address_service = MagicMock()
            response_object = MagicMock()
            response_object.json.return_value = [{
                "geometry": {
                    "type": "Point",
                    "coordinates": [1, 2]
                }
            }]
            address_service.get_by.return_value = response_object
            service.return_value = address_service
            result = search_for_location("Exeter")
            address_service.get_by.assert_called_with('text', "EXETER")
            self.assertEqual(result['location'], 'Exeter')
