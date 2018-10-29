from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from flask import url_for
from unittest.mock import patch
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.exceptions import ApplicationError
import json


class TestLocation(TestCase):

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_add_location_redirects_to_new(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_location'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    def test_add_location_renders(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_location'))

        self.assertStatus(response, 200)
        self.assert_template_used('location.html')
        self.assertFalse(self.mock_session.return_value.charge_added_outside_users_authority)

    def test_add_location_renders_with_previous_data(self):
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
        state.geometry = input

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_location'))

        self.assertStatus(response, 200)
        self.assert_template_used('location.html')
        self.assertIn('load_previous_data', response.data.decode())
        self.assertFalse(self.mock_session.return_value.charge_added_outside_users_authority)

    def test_add_location_post_redirects_to_new_when_state_none(self):
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

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_location'), data={'saved-features': input})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    def test_add_location_post_returns_required_validation(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_location'), data={'saved-features': None})

        self.assert_status(response, 400)
        self.assert_template_used('location.html')
        self.assertIn('is required', response.data.decode())

    def test_add_location_post_returns_count_validation(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        input_json = {"type": "FeatureCollection", "features": []}

        feature = {"type": "Feature",
                   "geometry": {
                       "type": "Polygon",
                       "coordinates": [
                           [[511076.08598934463, 381319.1389185938],
                            [502935.0162093069, 344754.81621829123],
                            [460299.51643357374, 365124.6766137525],
                            [478395.29646112275, 392099.3797708411],
                            [511076.08598934463, 381319.1389185938]]
                       ]},
                   "properties": {"id": 1}
                   }

        for _ in range(0, 501):
            input_json['features'].append(feature)

        input = json.dumps(input_json)

        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_location'), data={'saved-features': input})

        self.assert_status(response, 400)
        self.assert_template_used('location.html')
        self.assertIn('Delete a boundary to continue', response.data.decode())

    @patch('maintain_frontend.add_land_charge.location.ReviewRouter')
    def test_post_with_add_anywhere_permission_succeeds_when_data_set(self, mock_review_router):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        mock_review_router.get_redirect_url.return_value = url_for('add_land_charge.get_address_for_charge')

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
        self.mock_session.return_value.user.permissions = [Permissions.add_llc, Permissions.add_extent_anywhere]

        response = self.client.post(url_for('add_land_charge.post_location'), data={'saved-features': input})

        mock_review_router.update_edited_field.assert_called_with(
            'geometry', json.loads(input.strip())
        )

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_address_for_charge'))

    @patch('maintain_frontend.add_land_charge.location.ReviewRouter')
    def test_post_with_add_anywhere_permission_succeeds_when_address_data_set(self, mock_review_router):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        mock_review_router.get_redirect_url.return_value = url_for('add_land_charge.get_address_confirmation')

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

        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc, Permissions.add_extent_anywhere]

        response = self.client.post(url_for('add_land_charge.post_location'), data={
            'saved-features': input,
            'selected-address': json.dumps(selected_address)
        })

        mock_review_router.update_edited_field.assert_called_with(
            'geometry', json.loads(input.strip())
        )

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_address_confirmation'))

    @patch('maintain_frontend.add_land_charge.location.LocalAuthorityService')
    @patch('maintain_frontend.add_land_charge.location.ReviewRouter')
    def test_add_location_post_succeeds_when_no_address_and_in_authority(self, mock_review_router, mock_la_api):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        mock_review_router.get_redirect_url.return_value = url_for('add_land_charge.get_address_for_charge')

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
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.user.organisation = 'abc'

        mock_la_api.return_value.get_authorities_by_extent.return_value = {"abc": True}

        response = self.client.post(url_for('add_land_charge.post_location'), data={
            'saved-features': input
        })

        mock_review_router.update_edited_field.assert_called_with(
            'geometry', json.loads(input.strip())
        )

        mock_la_api.return_value.get_authorities_by_extent.assert_called()
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_address_for_charge'))

    @patch('maintain_frontend.add_land_charge.location.LocalAuthorityService')
    @patch('maintain_frontend.add_land_charge.location.ReviewRouter')
    def test_add_location_post_succeeds_when_address_data_set_if_in_authority(self, mock_review_router, mock_la_api):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        mock_review_router.get_redirect_url.return_value = url_for('add_land_charge.get_address_confirmation')

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

        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.user.organisation = 'abc'

        mock_la_api.return_value.get_authorities_by_extent.return_value = {"abc": True}

        response = self.client.post(url_for('add_land_charge.post_location'), data={
            'saved-features': input,
            'selected-address': json.dumps(selected_address)
        })

        mock_review_router.update_edited_field.assert_called_with(
            'geometry', json.loads(input.strip())
        )

        mock_la_api.return_value.get_authorities_by_extent.assert_called()
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_address_confirmation'))

    @patch('maintain_frontend.add_land_charge.location.LocalAuthorityService')
    @patch('maintain_frontend.add_land_charge.location.ReviewRouter')
    def test_add_location_post_redirects_to_location_confirmation(self, mock_review_router, mock_la_api):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        mock_review_router.get_redirect_url.return_value = url_for('add_land_charge.get_address_confirmation')

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

        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.user.organisation = 'Abc'

        mock_la_api.return_value.get_authorities_by_extent.return_value = {"DEF": True}

        response = self.client.post(url_for('add_land_charge.post_location'), data={
            'saved-features': input,
            'selected-address': json.dumps(selected_address)
        })

        mock_review_router.update_edited_field.assert_called_with(
            'geometry', json.loads(input.strip())
        )

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_location_confirmation', address_selected=True))

    @patch('maintain_frontend.add_land_charge.location.LocalAuthorityService')
    @patch('maintain_frontend.add_land_charge.location.ReviewRouter')
    def test_add_location_post_redirects_to_location_confirmation_no_address(self, mock_review_router, mock_la_api):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        mock_review_router.get_redirect_url.return_value = url_for('add_land_charge.get_address_confirmation')

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
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.user.organisation = 'Abc'

        mock_la_api.return_value.get_authorities_by_extent.return_value = {"DEF": True}

        response = self.client.post(url_for('add_land_charge.post_location'), data={
            'saved-features': input
        })

        mock_review_router.update_edited_field.assert_called_with(
            'geometry', json.loads(input.strip())
        )

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_location_confirmation', address_selected=False))

    @patch('maintain_frontend.add_land_charge.location.LocalAuthorityService')
    @patch('maintain_frontend.add_land_charge.location.ReviewRouter')
    def test_post_with_add_england_permission_succeeds_when_address_data_set_if_in_authority(self, mock_review_router,
                                                                                             mock_la_api):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        mock_review_router.get_redirect_url.return_value = url_for('add_land_charge.get_address_confirmation')

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

        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc, Permissions.add_extent_england]

        mock_la_api.return_value.get_authorities_by_extent.return_value = {"abc": True}

        response = self.client.post(url_for('add_land_charge.post_location'), data={
            'saved-features': input,
            'selected-address': json.dumps(selected_address)
        })

        mock_review_router.update_edited_field.assert_called_with(
            'geometry', json.loads(input.strip())
        )

        mock_la_api.return_value.get_authorities_by_extent.assert_called()
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_address_confirmation'))

    @patch('maintain_frontend.add_land_charge.location.LocalAuthorityService')
    @patch('maintain_frontend.add_land_charge.location.ReviewRouter')
    def test_post_with_add_england_permission_redirects_to_location_confirmation(self, mock_review_router,
                                                                                 mock_la_api):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        mock_review_router.get_redirect_url.return_value = url_for('add_land_charge.get_address_confirmation')

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

        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc, Permissions.add_extent_england]
        self.mock_session.return_value.user.organisation = 'Abc'

        mock_la_api.return_value.get_authorities_by_extent.return_value = []

        response = self.client.post(url_for('add_land_charge.post_location'), data={
            'saved-features': input,
            'selected-address': json.dumps(selected_address)
        })

        mock_review_router.update_edited_field.assert_called_with(
            'geometry', json.loads(input.strip())
        )

        mock_la_api.return_value.get_authorities_by_extent.assert_called()
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_location_confirmation', address_selected=True))

    @patch('maintain_frontend.add_land_charge.location.LocalAuthorityService')
    @patch('maintain_frontend.add_land_charge.location.ReviewRouter')
    def test_add_location_post_redirects_to_error(self, mock_review_router, mock_la_api):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        mock_review_router.get_redirect_url.return_value = url_for('add_land_charge.get_address_confirmation')

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
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.user.roles = ['LLC LA Admins']
        self.mock_session.return_value.user.organisation = 'Abc'

        mock_la_api.return_value.get_authorities_by_extent.side_effect = ApplicationError(500)

        response = self.client.post(url_for('add_land_charge.post_location'), data={
            'saved-features': input
        })

        mock_review_router.update_edited_field.assert_called_with(
            'geometry', json.loads(input.strip())
        )

        self.assert_status(response, 302)
        self.assertRedirects(response, '/error')

    def test_get_no_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = []

        response = self.client.get(url_for('add_land_charge.get_location'))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')

    def test_post_no_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = []

        response = self.client.post(url_for('add_land_charge.post_location'))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')

    @patch('maintain_frontend.add_land_charge.location.LocalAuthorityService')
    @patch('maintain_frontend.add_land_charge.location.ReviewRouter')
    def test_add_location_post_redirects_to_location_confirmation_no_address_if_address_invalid(self,
                                                                                                mock_review_router,
                                                                                                mock_la_api):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        mock_review_router.get_redirect_url.return_value = url_for('add_land_charge.get_address_confirmation')

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
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.user.roles = ['LLC LA Admins']
        self.mock_session.return_value.user.organisation = 'Abc'

        mock_la_api.return_value.get_authorities_by_extent.return_value = {"DEF": True}

        response = self.client.post(url_for('add_land_charge.post_location'), data={
            'saved-features': input,
            'selected-address': '{"hello":"world"}'
        })

        mock_review_router.update_edited_field.assert_called_with(
            'geometry', json.loads(input.strip())
        )

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_location_confirmation', address_selected=False))
