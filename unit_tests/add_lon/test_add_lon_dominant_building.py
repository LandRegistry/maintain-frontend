from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from flask import url_for
from unittest.mock import patch
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LightObstructionNoticeItem
from unit_tests.mock_data.mock_land_charges import get_mock_lon_item

TEMPLATE = 'dominant_building.html'

ADD_LON = 'add_lon.'
GET_DOMINANT_BUILDING = ADD_LON + 'get_dominant_building_info'
POST_DOMINANT_BUILDING = ADD_LON + 'post_dominant_building'
GET_DOMINANT_BUILDING_EXTENT = ADD_LON + 'get_dominant_building_extent'

NO_VALIDATION_ERRORS = []
ERROR_MESSAGE = ['some error message']

INVALID_STRING = ""
VALID_STRING = "string"
VALID_POSTCODE = "EX4 7AN"


class TestLONDominantBuilding(TestCase):
    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_dominant_building_redirects_to_new_when_state_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.add_lon_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        response = self.client.get(url_for(GET_DOMINANT_BUILDING))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for(ADD_LON + 'new'))

    def test_dominant_building_get(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LightObstructionNoticeItem()
        self.mock_session.add_lon_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        response = self.client.get(url_for(GET_DOMINANT_BUILDING))

        self.assert_status(response, 200)
        self.assert_template_used(TEMPLATE)

    def test_dominant_building_no_permission_redirects(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.user.permissions = []

        response = self.client.get(url_for(GET_DOMINANT_BUILDING))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')

        response = self.client.get(url_for(POST_DOMINANT_BUILDING))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')

    @patch('maintain_frontend.add_lon.dominant_building.ReviewRouter')
    @patch('maintain_frontend.add_lon.dominant_building.request')
    @patch('maintain_frontend.add_lon.dominant_building.DominantAddressValidator')
    def test_post_valid_address(self, mock_validator, mock_request, mock_review_router):

        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]
        mock_lon = LightObstructionNoticeItem.from_json(get_mock_lon_item())
        self.mock_session.return_value.add_lon_charge_state = mock_lon

        mock_review_router.get_redirect_url.return_value = url_for(GET_DOMINANT_BUILDING_EXTENT)

        mock_request.form = {
            'have_address': 'Yes',
            'postcode': 'CHANGED',
            'uprn': '123',
            'address_line_1': '1 The Road',
            'address_line_2': 'Test',
            'address_line_3': 'Foo',
            'address_line_4': 'Test',
            'address_line_5': 'Test',
            'address_line_6': 'Test'
        }
        mock_validator.validate.return_value.errors = None

        response = self.client.post(url_for(POST_DOMINANT_BUILDING))

        self.assert_status(response, 302)
        self.assertEqual(self.mock_session.return_value.add_lon_charge_state.charge_address['postcode'],
                         'CHANGED')
        self.assertEqual(self.mock_session.return_value.add_lon_charge_state.charge_geographic_description,
                         '')
        self.assertRedirects(response, url_for(GET_DOMINANT_BUILDING_EXTENT))

    @patch('maintain_frontend.add_lon.dominant_building.ReviewRouter')
    @patch('maintain_frontend.add_lon.dominant_building.request')
    @patch('maintain_frontend.add_lon.dominant_building.DominantAddressValidator')
    def test_post_valid_description(self, mock_validator, mock_request, mock_review_router):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]
        mock_lon = LightObstructionNoticeItem.from_json(get_mock_lon_item())
        self.mock_session.return_value.add_lon_charge_state = mock_lon

        mock_review_router.get_redirect_url.return_value = url_for(GET_DOMINANT_BUILDING_EXTENT)

        mock_request.form = {
            'have_address': 'No',
            'charge_geographic_description': 'CHANGED'
        }
        mock_validator.validate.return_value.errors = None

        response = self.client.post(url_for(POST_DOMINANT_BUILDING))

        self.assert_status(response, 302)
        self.assertEqual(self.mock_session.return_value.add_lon_charge_state.charge_address,
                         '')
        self.assertEqual(self.mock_session.return_value.add_lon_charge_state.charge_geographic_description,
                         'CHANGED')
        self.assertRedirects(response, url_for(GET_DOMINANT_BUILDING_EXTENT))

    @patch('maintain_frontend.add_lon.dominant_building.request')
    @patch('maintain_frontend.add_lon.dominant_building.DominantAddressValidator')
    def test_post_invalid_data(self, mock_validator, mock_request):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        error = {'postcode': ERROR_MESSAGE}
        mock_validator.validate.return_value.errors = error

        mock_request.form = {}

        response = self.client.post(url_for(POST_DOMINANT_BUILDING))

        self.assert_context('validation_errors', error)
        self.assert_status(response, 400)
        self.assert_template_used(TEMPLATE)
