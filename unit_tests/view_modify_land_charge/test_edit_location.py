from maintain_frontend import main
from flask_testing import TestCase
from flask import url_for
from unit_tests.utilities import Utilities
from unittest.mock import patch
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.constants.permissions import Permissions
import json


class TestEditLocation(TestCase):

    def create_app(self):
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def test_edit_location_get_with_state(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        state = LocalLandChargeItem()
        state.geometry = 'abc'
        self.mock_session.return_value.add_charge_state = state

        response = self.client.get(url_for('modify_land_charge.get_location'))
        self.assert_status(response, 200)
        self.assert_template_used('location.html')

    def test_edit_location_get_without_geom(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        state = LocalLandChargeItem()
        self.mock_session.return_value.add_charge_state = state

        response = self.client.get(url_for('modify_land_charge.get_location'))
        self.assert_status(response, 200)
        self.assert_template_used('location.html')

    def test_edit_location_get_without_state(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        self.mock_session.return_value.add_charge_state = None

        response = self.client.get(url_for('modify_land_charge.get_location'))
        self.assert_status(response, 302)
        self.assertRedirects(response, '/error')

    def test_location_post_without_state(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        self.mock_session.return_value.add_charge_state = None
        response = self.client.post(url_for('modify_land_charge.post_location'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/error')

    @patch('maintain_frontend.view_modify_land_charge.edit_location.AddLocationMapValidator')
    def test_location_post_validation_errors(self, mock_location_validator):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        state = LocalLandChargeItem()
        state.geometry = "abc"

        self.mock_session.return_value.add_charge_state = state
        validation_errors = {'map': 'test error message'}
        mock_location_validator.validate.return_value.errors = validation_errors
        response = self.client.post(url_for('modify_land_charge.post_location'))

        self.assert_status(response, 400)
        self.assert_context('validation_errors', validation_errors)

    def test_location_post_success(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        self.mock_session.return_value.user.roles = ['LLC LR Admins']

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.local_land_charge = 12345678

        self.mock_session.return_value.add_charge_state = state
        geometry = {'coordinates': [294230.7392612094, 93185.05361812815], 'type': 'Point'}
        form_data = {'saved-features': json.dumps({'features': [{'geometry': geometry}]})}
        response = self.client.post(url_for('modify_land_charge.post_location'), data=form_data)

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('modify_land_charge.modify_land_charge', local_land_charge='LLC-FCDPP'))

    @patch('maintain_frontend.view_modify_land_charge.edit_location.LocalAuthorityService')
    def test_edit_location_post_redirects_to_location_confirmation(self, mock_la_api):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        input = '{"type":"FeatureCollection",' \
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

        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        self.mock_session.return_value.user.roles = ['LLC LA Admins']
        self.mock_session.return_value.user.organisation = 'Abc'

        mock_la_api.return_value.get_authorities_by_extent.return_value = {"DEF"}

        response = self.client.post(url_for('modify_land_charge.post_location'), data={
            'saved-features': input
        })

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('modify_land_charge.get_location_confirmation'))
