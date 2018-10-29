import json
from io import BytesIO
from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from unittest.mock import patch
from flask import url_for, g
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.add_land_charge.upload_shapefile import parse_upload

UPLOAD_SHAPEFILE_PATH = 'maintain_frontend.add_land_charge.upload_shapefile'


class TestUploadShapefile(TestCase):

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_get_upload_shapefile_valid(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_upload_shapefile'))

        self.assert_status(response, 200)
        self.assert_template_used('upload_shapefile.html')

    def test_get_upload_shapefile_no_state(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_upload_shapefile'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    def test_post_save_existing_geometries_with_saved_features(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        input = "{\"key\": \"value\"}"

        response = self.client.post(url_for('add_land_charge.post_save_existing_geometries'),
                                    data={'saved-features-upload': input})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_upload_shapefile'))
        self.assertEqual(g.session.add_charge_state.geometry, json.loads(input))

    def test_post_save_existing_geometries_without_saved_features(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_save_existing_geometries'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_upload_shapefile'))
        self.assertIsNone(g.session.add_charge_state.geometry)

    @patch('{}.fiona.BytesCollection'.format(UPLOAD_SHAPEFILE_PATH))
    @patch('{}.datetime'.format(UPLOAD_SHAPEFILE_PATH))
    def test_parse_upload(self, datetime_mock, bytes_collection_mock):
        mock_shape_collection = [
            {'geometry': 'valid geometry'},
            {'geometry': 'another valid geometry'}
        ]

        timestamp = 100000000
        datetime_mock.datetime.now.return_value.timestamp.return_value = timestamp
        expected_id = timestamp * 1000

        bytes_collection_mock.return_value.__enter__.return_value = mock_shape_collection
        result = parse_upload(BytesIO())

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['properties']['id'], expected_id)
        self.assertEqual(result[0]['geometry'], mock_shape_collection[0]['geometry'])
        self.assertEqual(result[1]['properties']['id'], expected_id + 1)
        self.assertEqual(result[1]['geometry'], mock_shape_collection[1]['geometry'])

    @patch('{}.parse_upload'.format(UPLOAD_SHAPEFILE_PATH))
    @patch('{}.UploadShapefileValidator'.format(UPLOAD_SHAPEFILE_PATH))
    def test_post_upload_geometries_valid_existing_geometries(self, validator_mock, parse_upload_mock):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        geometry = {
            'features': ['feature']
        }

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.add_charge_state.geometry = geometry
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        validator_mock.validate.return_value.errors = None
        parse_upload_mock.return_value = []

        response = self.client.post(url_for('add_land_charge.post_upload_shapefile'), data={
            'shapefile-input': BytesIO(b'shapes')
        })

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_location', upload=True))
        self.assertEqual(g.session.add_charge_state.geometry, geometry)

    @patch('{}.parse_upload'.format(UPLOAD_SHAPEFILE_PATH))
    @patch('{}.UploadShapefileValidator'.format(UPLOAD_SHAPEFILE_PATH))
    def test_post_upload_geometries_valid_no_geometries(self, validator_mock, parse_upload_mock):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.add_charge_state.geometry = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        validator_mock.validate.return_value.errors = None
        parse_upload_mock.return_value = []

        response = self.client.post(url_for('add_land_charge.post_upload_shapefile'), data={
            'shapefile-input': BytesIO(b'shapes')
        })

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_location', upload=True))
        self.assertIsNotNone(g.session.add_charge_state.geometry)

    def test_post_upload_geometries_no_charge_state(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_upload_shapefile'), data={
            'shapefile-input': BytesIO(b'shapes')
        })

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    def test_post_upload_geometries_validation_error(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_upload_shapefile'), data=None)

        self.assert_status(response, 200)
        self.assertTemplateUsed("upload_shapefile.html")
        self.assertIn('Upload a file', response.data.decode())
