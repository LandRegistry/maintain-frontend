from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from flask import url_for
from unittest.mock import patch
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LightObstructionNoticeItem

TEMPLATE = 'dominant_building_extent.html'

ADD_LON = 'add_lon.'
GET_DOMINANT_EXTENT = ADD_LON + 'get_dominant_building_extent'
POST_DOMINANT_EXTENT = ADD_LON + 'post_dominant_building_extent'
GET_LAND_INTEREST = ADD_LON + 'get_land_interest'

NO_VALIDATION_ERRORS = []
ERROR_MESSAGE = ['draw the extent']
POSTCODE = "EX4 7AN"
POSTCODE_JSON = '{"postcode": "EX4 7AN"}'

VALID_FEATURE = '{"type":"FeatureCollection",' \
                '"features":[' \
                '{"type":"Feature",' \
                '"geometry":{' \
                '"type":"Polygon",' \
                '"coordinates":[' \
                '[[511076.08598934463,381319.1389185938],' \
                '[502935.0162093069,344754.81621829123],' \
                '[460299.51643357374,365124.6766137525],' \
                '[478395.29646112275,392099.3797708411],' \
                '[511076.08598934463,381319.1389185938]]]},' \
                '"properties":{"id":1}}]}'

EMPTY_FEATURE = None


class TestLONDominantBuildingExtent(TestCase):
    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_dominant_building_extent_redirects_to_new_when_state_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.add_lon_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        response = self.client.get(url_for(GET_DOMINANT_EXTENT))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for(ADD_LON + 'new'))

    def test_dominant_building_extent_get(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LightObstructionNoticeItem()
        self.mock_session.add_lon_charge_state = state
        self.mock_session.return_value.add_lon_charge_state.charge_address = {"postcode": "EX4 7AN"}
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        response = self.client.get(url_for(GET_DOMINANT_EXTENT))

        self.assert_status(response, 200)
        self.assert_template_used(TEMPLATE)

    def test_dominant_extent_no_permission_redirects(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.user.permissions = []

        response = self.client.get(url_for(GET_DOMINANT_EXTENT))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')

        response = self.client.get(url_for(POST_DOMINANT_EXTENT))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')

    @patch('maintain_frontend.add_lon.dominant_building_extent.ReviewRouter')
    @patch('maintain_frontend.add_lon.dominant_building_extent.AddLocationMapValidator')
    def test_successful_post(self, mock_validator, mock_review_router):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.add_lon_charge_state.charge_address = {"postcode": "EX4 7AN"}
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]
        mock_review_router.get_redirect_url.return_value = url_for(GET_LAND_INTEREST)

        mock_validator.validate.return_value.errors = NO_VALIDATION_ERRORS

        data = {'saved-features': VALID_FEATURE}
        response = self.client.post(url_for(POST_DOMINANT_EXTENT), data=data)

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for(GET_LAND_INTEREST))

    @patch('maintain_frontend.add_lon.dominant_building_extent.AddLocationMapValidator')
    def test_post_with_missing_features(self, mock_validator):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.add_lon_charge_state.charge_address = {"postcode": "EX4 7AN"}
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        error = {'map': ERROR_MESSAGE}
        mock_validator.validate.return_value.errors = error

        data = {'saved-features': EMPTY_FEATURE}
        response = self.client.post(url_for(POST_DOMINANT_EXTENT), data=data)

        self.assert_context("postcode", POSTCODE)
        self.assert_context("validation_errors", error)
        self.assert_status(response, 400)
        self.assert_template_used(TEMPLATE)
