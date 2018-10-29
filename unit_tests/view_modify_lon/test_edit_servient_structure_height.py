from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from flask import url_for
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.models import LightObstructionNoticeItem
from unit_tests.mock_data.mock_land_charges import get_mock_lon_item
from unittest.mock import patch


class TestEditServientStructureHeight(TestCase):
    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_edit_servient_structure_height_get_with_state(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]
        mock_lon = LightObstructionNoticeItem.from_json(get_mock_lon_item())
        self.mock_session.return_value.add_lon_charge_state = mock_lon

        response = self.client.get(url_for('modify_lon.edit_servient_structure_height_get'))

        self.assert_status(response, 200)
        self.assert_template_used('servient_structure_height.html')

    def test_edit_servient_structure_height_get_with_no_state(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]
        self.mock_session.return_value.add_lon_charge_state = None

        response = self.client.get(url_for('modify_lon.edit_servient_structure_height_get'))

        self.assert_status(response, 302)

    @patch('maintain_frontend.view_modify_lon.edit_servient_structure_height.request')
    @patch('maintain_frontend.view_modify_lon.edit_servient_structure_height.ServientStructureHeightValidator')
    def test_edit_servient_structure_height_update_success(self, mock_validator, mock_request):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]

        mock_lon = LightObstructionNoticeItem.from_json(get_mock_lon_item())

        self.mock_session.return_value.add_lon_charge_state = mock_lon
        self.mock_session.return_value.edited_fields = {}

        mock_validator.validate.return_value.errors = None
        mock_request.form.get.return_value = "10"

        response = self.client.post(url_for('modify_lon.edit_servient_structure_height_post'))

        structure_position_and_dimension = \
            self.mock_session.return_value.add_lon_charge_state.structure_position_and_dimension

        self.assert_status(response, 302)
        self.assertEqual(structure_position_and_dimension["height"],
                         "10")
        self.assertEqual(self.mock_session.return_value.edited_fields['structure-dimension'],
                         "Height - planned development")

    @patch('maintain_frontend.view_modify_lon.edit_servient_structure_height.request')
    @patch('maintain_frontend.view_modify_lon.edit_servient_structure_height.ServientStructureHeightValidator')
    def test_edit_servient_structure_height_update_success_amend(self, mock_validator, mock_request):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]

        mock_lon = LightObstructionNoticeItem.from_json(get_mock_lon_item())
        mock_lon.structure_position_and_dimension['height'] = '20'
        mock_lon.structure_position_and_dimension['units'] = 'Metres'

        self.mock_session.return_value.add_lon_charge_state = mock_lon
        self.mock_session.return_value.edited_fields = {}

        mock_validator.validate.return_value.errors = None
        mock_request.form.get.return_value = "Unlimited height"

        response = self.client.post(url_for('modify_lon.edit_servient_structure_height_post'))

        structure_position_and_dimension = \
            self.mock_session.return_value.add_lon_charge_state.structure_position_and_dimension

        self.assert_status(response, 302)
        self.assertEqual(structure_position_and_dimension["height"],
                         "Unlimited height")
        self.assertEqual(self.mock_session.return_value.edited_fields['structure-dimension'],
                         "Height - planned development")

    @patch('maintain_frontend.view_modify_lon.edit_servient_structure_height.ServientStructureHeightValidator')
    def test_edit_servient_structure_height_update_errors(self, mock_validator):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]

        self.mock_session.return_value.add_lon_charge_state = LightObstructionNoticeItem()
        mock_validator.validate.return_value.errors = {"error": "test-error"}

        response = self.client.post(url_for('modify_lon.edit_servient_structure_height_post'))

        self.assert_status(response, 400)
        self.assert_template_used('servient_structure_height.html')
        self.assert_context("validation_errors", {"error": "test-error"})

    @patch('maintain_frontend.view_modify_lon.edit_servient_structure_height.request')
    @patch('maintain_frontend.view_modify_lon.edit_servient_structure_height.ServientStructureHeightValidator')
    def test_edit_servient_structure_position_and_dimension_unlimited_height(self, mock_validator, mock_request):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]

        mock_lon = LightObstructionNoticeItem.from_json(get_mock_lon_item())
        del(mock_lon.structure_position_and_dimension['height'])

        self.mock_session.return_value.add_lon_charge_state = mock_lon
        self.mock_session.return_value.edited_fields = {}

        mock_validator.validate.return_value.errors = None
        mock_request.form.get.return_value = "Unlimited height"

        response = self.client.post(url_for('modify_lon.edit_servient_structure_height_post'))

        structure_position_and_dimension = \
            self.mock_session.return_value.add_lon_charge_state.structure_position_and_dimension

        self.assert_status(response, 302)
        self.assertEqual(structure_position_and_dimension["height"],
                         "Unlimited height")
        self.assertEqual(self.mock_session.return_value.edited_fields['structure-dimension'],
                         "Height - planned development")

    @patch('maintain_frontend.view_modify_lon.edit_servient_structure_height.request')
    @patch('maintain_frontend.view_modify_lon.edit_servient_structure_height.ServientStructureHeightValidator')
    def test_edit_servient_structure_position_and_dimension_set_height(self, mock_validator, mock_request):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]

        mock_lon = LightObstructionNoticeItem.from_json(get_mock_lon_item())
        del(mock_lon.structure_position_and_dimension['height'])

        self.mock_session.return_value.add_lon_charge_state = mock_lon
        self.mock_session.return_value.edited_fields = {}

        mock_validator.validate.return_value.errors = None
        mock_request.form.get.return_value = "10"

        response = self.client.post(url_for('modify_lon.edit_servient_structure_height_post'))

        structure_position_and_dimension = \
            self.mock_session.return_value.add_lon_charge_state.structure_position_and_dimension

        self.assert_status(response, 302)
        self.assertEqual(structure_position_and_dimension["height"],
                         "10")
        self.assertEqual(self.mock_session.return_value.edited_fields['structure-dimension'],
                         "Height - planned development")
