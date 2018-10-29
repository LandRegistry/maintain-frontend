from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from unittest.mock import patch, MagicMock
from flask import url_for, g
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.models import LightObstructionNoticeItem
from unit_tests.mock_data.mock_land_charges import get_mock_lon_item

uploaded_form_b_response = {
    "form-b": [
        {
            "bucket": "lon",
            "file_id": "form_b_id",
            "reference": "lon/form_b_id?subdirectories=test_sub_directory",
            "subdirectory": "test_sub_directory"
        }
    ]
}

uploaded_form_a_response = {
    "form-a": [
        {
            "bucket": "lon",
            "file_id": "form_a_id",
            "reference": "lon/form_a_id?subdirectories=test_sub_directory",
            "subdirectory": "test_sub_directory"
        }
    ]
}


class TestCancelLONCharge(TestCase):

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    @patch('maintain_frontend.view_modify_lon.cancel_lon.LocalLandChargeService')
    def test_cancel_get_not_found(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.cancel_lon]
        mock_response = MagicMock()
        mock_service.return_value.get_by_charge_number.return_value = mock_response
        mock_response.status_code = 404

        response = self.client.get(url_for('cancel_lon.cancel_get', charge_id='LLC-TST'))

        self.assert_status(response, 302)

    @patch('maintain_frontend.view_modify_lon.cancel_lon.LocalLandChargeService')
    def test_cancel_get_found(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.cancel_lon]

        mock_response = MagicMock()
        mock_service.return_value.get_by_charge_number.return_value = mock_response
        mock_response.status_code = 200
        mock_response.json.return_value = [{"item": get_mock_lon_item(), "display_id": "LLC-TST"}]

        response = self.client.get(url_for('cancel_lon.cancel_get', charge_id='LLC-TST'))

        self.assert_status(response, 200)

    @patch('maintain_frontend.view_modify_lon.cancel_lon.CancelLonValidator')
    @patch('maintain_frontend.view_modify_lon.cancel_lon.LocalLandChargeService')
    def test_cancel_upload_post_failed_validation(self, mock_service, mock_validator):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.cancel_lon]

        mock_response = MagicMock()
        mock_service.return_value.get_by_charge_number.return_value = mock_response
        mock_response.status_code = 200
        mock_response.json.return_value = [{"item": get_mock_lon_item(), "display_id": "LLC-TST"}]

        validation_errors = {"error": "Something went wrong"}
        mock_validator.validate.return_value.errors = validation_errors

        response = self.client.post(url_for('cancel_lon.cancel_post', charge_id='LLC-TST'))

        self.assert_status(response, 400)
        self.assert_context('validation_errors', validation_errors)

    @patch('maintain_frontend.view_modify_lon.cancel_lon.StorageAPIService')
    @patch('maintain_frontend.view_modify_lon.cancel_lon.CancelLonValidator')
    @patch('maintain_frontend.view_modify_lon.cancel_lon.LocalLandChargeService')
    @patch('maintain_frontend.view_modify_lon.cancel_lon.request')
    def test_cancel_upload_post_success(self, mock_request, mock_llc_service, mock_validator, mock_storage_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.cancel_lon]

        mock_response = MagicMock()
        mock_llc_service.return_value.get_by_charge_number.return_value = mock_response
        mock_response.status_code = 200
        mock_response.json.return_value = [{"item": get_mock_lon_item(), "display_id": "LLC-TST"}]

        mock_request.form.getlist.return_value = ["Form B"]

        mock_storage_service.return_value.save_files.return_value.json.return_value = uploaded_form_b_response

        mock_validator.validate.return_value.errors = None
        g.session = self.mock_session

        response = self.client.post(url_for('cancel_lon.cancel_post', charge_id='LLC-TST'))

        expected_charge_document_state = {
            "form-a": uploaded_form_a_response["form-a"],
            "form-b": uploaded_form_b_response["form-b"],
        }

        print(g.session.add_lon_charge_state.documents_filed)
        self.assertEqual(g.session.add_lon_charge_state.documents_filed, expected_charge_document_state)
        self.assert_status(response, 302)

    @patch('maintain_frontend.view_modify_lon.cancel_lon.AuditAPIService')
    @patch('maintain_frontend.view_modify_lon.cancel_lon.MaintainApiService')
    @patch('maintain_frontend.view_modify_lon.cancel_lon.LocalLandChargeService')
    def test_cancel_confirm_success(self, mock_service, mock_maintain_api, mock_audit):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.cancel_lon]
        self.mock_session.add_lon_charge_state = LightObstructionNoticeItem()
        g.session = self.mock_session

        mock_response = MagicMock()
        mock_service.return_value.get_by_charge_number.return_value = mock_response
        mock_response.status_code = 200
        mock_response.json.return_value = [{"item": get_mock_lon_item(), "display_id": "LLC-TST"}]

        response = self.client.post(url_for('cancel_lon.confirm', charge_id='LLC-TST'))

        mock_maintain_api.update_charge.assert_called_with(g.session.add_lon_charge_state)
        mock_audit.audit_event.assert_called_with('Cancelling charge', supporting_info={'id': 'LLC-TST'})
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('cancel_lon.charge_cancelled', charge_id='LLC-TST'))
