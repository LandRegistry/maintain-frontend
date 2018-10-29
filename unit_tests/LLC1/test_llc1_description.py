from flask_testing import TestCase
from unit_tests.utilities import Utilities
from unittest.mock import MagicMock, patch
from maintain_frontend import main
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.models import LLC1Search
from maintain_frontend.main import app
from flask import url_for, g
import json


class TestLLC1Description(TestCase):
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

        response = self.client.get(url_for("create_llc1.llc1_get_description"))
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for("create_llc1.create_llc1"))

    def test_get_renders_when_state_ok(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.llc1_state = LLC1Search()
        self.mock_session.return_value.user.permissions = [Permissions.request_llc1]

        response = self.client.get(url_for("create_llc1.llc1_get_description"))
        self.assert_status(response, 200)
        self.assert_template_used("search_description.html")

    def test_post_redirects_when_no_state(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.llc1_state = None
        self.mock_session.return_value.user.permissions = [Permissions.request_llc1]

        response = self.client.post(url_for("create_llc1.llc1_set_description"),
                                    data={'charge-geographic-description': 'foo', 'hasAddress': None})
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for("create_llc1.create_llc1"))

    def test_post_renders_error_when_no_description(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.llc1_state = LLC1Search()
        self.mock_session.return_value.user.permissions = [Permissions.request_llc1]
        response = self.client.post(url_for("create_llc1.llc1_set_description"),
                                    data={'has-address': 'No', 'charge-geographic-description': ''})
        self.assertStatus(response, 400)
        self.assert_template_used('search_description.html')

    @patch('maintain_frontend.app.requests.Session')
    @patch('maintain_frontend.add_land_charge.address_confirmation.AddressConverter')
    def test_post_redirects_when_single_address_chosen(self, session, mock_address_converter):
        with app.test_request_context():
            self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
            self.mock_session.return_value.llc1_state = LLC1Search()
            self.mock_session.return_value.user.permissions = [Permissions.request_llc1]

            g.session = MagicMock()
            response = MagicMock()
            response.status_code = 201
            session.return_value.post.return_value = response
            selected_address = {
                'address': 'display address',
                'line_1': 'Flat 1',
                'line_2': 'Place',
                'line_3': 'Holder',
                'line_4': 'Flat 1',
                'line_5': 'Flat 1',
                'line_6': 'Flat 1',
                'postcode': 'postcode',
                'uprn': 123456789
            }

            mock_address_converter.to_charge_address.return_value = selected_address

            response = self.client.post(url_for("create_llc1.llc1_set_description"), data={
                'has-address': 'ProvideAddress',
                'selected-address': json.dumps(selected_address),
            })
            self.assertEqual(self.mock_session.return_value.llc1_state.description, 'Flat 1, Place, Holder, Flat 1, '
                                                                                    'Flat 1, Flat 1 postcode')
            self.assert_status(response, 302)
            self.assertRedirects(response, url_for("create_llc1.llc1_get_result"))

    @patch('maintain_frontend.app.requests.Session')
    def test_post_redirects_when_no_single_address_chosen_with_description(self, session):
        with app.test_request_context():
            self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
            self.mock_session.return_value.llc1_state = LLC1Search()
            self.mock_session.return_value.user.permissions = [Permissions.request_llc1]

            g.session = MagicMock()
            response = MagicMock()
            response.status_code = 201
            session.return_value.post.return_value = response

            response = self.client.post(url_for("create_llc1.llc1_set_description"), data={
                'has-address': 'No',
                'charge-geographic-description': 'This is a valid description',
            })

            self.assertEqual(self.mock_session.return_value.llc1_state.description, 'This is a valid description')
            self.assert_status(response, 302)
            self.assertRedirects(response, url_for("create_llc1.llc1_get_result"))

    def test_get_without_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = []
        response = self.client.get(url_for("create_llc1.llc1_get_description"))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')

    def test_post_without_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = []
        response = self.client.post(url_for("create_llc1.llc1_set_description"),
                                    data={'charge-geographic-description': '', 'hasAddress': 'No'})
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')
