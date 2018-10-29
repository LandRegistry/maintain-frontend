from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from unittest.mock import patch, MagicMock
from flask import url_for
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LightObstructionNoticeItem
from maintain_frontend.constants.permissions import Permissions
import datetime
from dateutil.relativedelta import relativedelta
from unit_tests.mock_data.mock_land_charges import get_mock_lon_item


class TestModifyLON(TestCase):

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    @patch('maintain_frontend.view_modify_lon.modify_lon.LocalLandChargeService')
    def test_modify_lon_upload_get_invalid_id(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]

        response = self.client.get(url_for('modify_lon.modify_lon_upload_get', charge_id=123))
        self.assert_status(response, 302)

    @patch('maintain_frontend.view_modify_lon.modify_lon.LocalLandChargeService')
    def test_modify_lon_upload_cancelled(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]

        self.mock_session.return_value.add_lon_charge_state = None
        mock_item = get_mock_lon_item().copy()
        mock_item['end-date'] = '2017-01-01'
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            "item": mock_item,
            "display_id": "LLC-TST",
            "cancelled": True
        }]

        mock_service.return_value.get_by_charge_number.return_value = mock_response

        response = self.client.get(url_for('modify_lon.modify_lon_upload_get', charge_id='LLC-TST'))
        self.assert_redirects(response, '/error')

    @patch('maintain_frontend.view_modify_lon.modify_lon.LocalLandChargeService')
    def test_modify_lon_upload_get_found(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]

        self.mock_session.return_value.add_lon_charge_state = None
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            "item": get_mock_lon_item(), "display_id": "LLC-TST", "cancelled": False
        }]

        mock_service.return_value.get_by_charge_number.return_value = mock_response

        response = self.client.get(url_for('modify_lon.modify_lon_upload_get', charge_id='LLC-TST'))

        self.assert_status(response, 200)

    @patch('maintain_frontend.view_modify_lon.modify_lon.LocalLandChargeService')
    def test_modify_lon_upload_get_not_found(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]
        self.mock_session.return_value.add_lon_charge_state = None

        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_service.return_value.get_by_charge_number.return_value = mock_response

        response = self.client.get(url_for('modify_lon.modify_lon_upload_get', charge_id='LLC-TST'))

        self.assert_status(response, 302)

    @patch('maintain_frontend.view_modify_lon.modify_lon.LocalLandChargeService')
    def test_modify_lon_redirect_when_different_id_in_session(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]

        state = LightObstructionNoticeItem.from_json(get_mock_lon_item())
        self.mock_session.return_value.add_lon_charge_state = state

        response = self.client.get(url_for('modify_lon.modify_lon_upload_get', charge_id=3))

        self.assert_status(response, 302)

    @patch('maintain_frontend.view_modify_lon.modify_lon.VaryLonValidator')
    @patch('maintain_frontend.view_modify_lon.modify_lon.LocalLandChargeService')
    def test_upload_lon_documents_no_select(self, mock_service, mock_validator):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"item": get_mock_lon_item(), "display_id": "LLC-TST", "cancelled": False}]
        mock_service.return_value.get_by_charge_number.return_value = mock_response

        mock_validator.validate.return_value.errors = {'vary-lon-options': ['Choose one']}

        response = self.client.post(url_for('modify_lon.modify_lon_upload_post', charge_id="LLC-TST"))

        self.assert_context('validation_errors', {'vary-lon-options': ['Choose one']})
        self.assert_status(response, 400)
        self.assert_template_used('modify_lon_upload.html')

    @patch('maintain_frontend.view_modify_lon.modify_lon.handle_vary_lon_options_choice')
    @patch('maintain_frontend.view_modify_lon.modify_lon.VaryLonValidator')
    @patch('maintain_frontend.view_modify_lon.modify_lon.LocalLandChargeService')
    def test_upload_lon_documents_no_errors(self, mock_service, mock_validator, mock_handle_options):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"item": get_mock_lon_item(), "display_id": "LLC-TST", "cancelled": False}]
        mock_service.return_value.get_by_charge_number.return_value = mock_response

        mock_validator.validate.return_value.errors = None

        response = self.client.post(url_for('modify_lon.modify_lon_upload_post', charge_id="LLC-TST"))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('modify_lon.modify_lon_details_get', charge_id="LLC-TST"))

    @patch('maintain_frontend.view_modify_lon.modify_lon.request')
    @patch('maintain_frontend.view_modify_lon.modify_lon.VaryLonValidator')
    @patch('maintain_frontend.view_modify_lon.modify_lon.StorageAPIService')
    @patch('maintain_frontend.view_modify_lon.modify_lon.LocalLandChargeService')
    def test_upload_definitive_certificate_fields(self, mock_service, mock_storage_service, mock_validator,
                                                  mock_request):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]

        state = LightObstructionNoticeItem()
        self.mock_session.return_value.add_lon_charge_state = state
        self.mock_session.return_value.edited_fields = {}

        expected_expiry_date = datetime.date.today() + relativedelta(years=+21)
        expected_definitive_date = datetime.date(1, 1, 1)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"item": get_mock_lon_item(), "display_id": "LLC-TST", "cancelled": False}]
        mock_service.return_value.get_by_charge_number.return_value = mock_response

        mock_validator.validate.return_value.errors = None

        mock_request.form.getlist.return_value = ["Definitive Certificate"]
        mock_request.form.get('definitive_cert_day').return_value = 1
        mock_request.form.get('definitive_cert_month').return_value = 1
        mock_request.form.get('definitive_cert_year').return_value = 1
        mock_request.files.get('definitive-certificate-file-input').return_value = True

        response = self.client.post(url_for('modify_lon.modify_lon_upload_post', charge_id="LLC-TST"))

        self.assertEqual(self.mock_session.return_value.add_lon_charge_state.expiry_date,
                         expected_expiry_date)
        self.assertEqual(self.mock_session.return_value.add_lon_charge_state.tribunal_definitive_certificate_date,
                         expected_definitive_date)
        self.assertEqual(self.mock_session.return_value.edited_fields['tribunal-definitive-certificate-date'],
                         "Tribunal definitive certificate date")
        self.assertEqual(self.mock_session.return_value.edited_fields['expiry-date'],
                         "Expiry date")
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('modify_lon.modify_lon_details_get', charge_id="LLC-TST"))

    @patch('maintain_frontend.view_modify_lon.modify_lon.request')
    @patch('maintain_frontend.view_modify_lon.modify_lon.LocalLandChargeService')
    def test_vary_lon_validator_no_option_selected(self, mock_service, mock_request):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]
        self.mock_session.return_value.edited_fields = {}

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"item": get_mock_lon_item(), "display_id": "LLC-TST", "cancelled": False}]
        mock_service.return_value.get_by_charge_number.return_value = mock_response

        mock_request.form.getlist.return_value = []

        response = self.client.post(url_for('modify_lon.modify_lon_upload_post', charge_id="LLC-TST"))

        context_validation_error = self.get_context_variable('validation_errors')

        self.assert_status(response, 400)
        self.assertIsNotNone(context_validation_error["vary-lon-options"])
        self.assertEqual(context_validation_error["vary-lon-options"].inline_message, "Choose one option")

    @patch('maintain_frontend.view_modify_lon.modify_lon.request')
    @patch('maintain_frontend.view_modify_lon.modify_lon.LocalLandChargeService')
    def test_vary_lon_validator_required_fields_definitive_certificate(self, mock_service, mock_request):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]
        self.mock_session.return_value.edited_fields = {}

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"item": get_mock_lon_item(), "display_id": "LLC-TST", "cancelled": False}]
        mock_service.return_value.get_by_charge_number.return_value = mock_response

        mock_request.form.getlist.return_value = ["Definitive Certificate"]
        mock_request.form.get.return_value = ""
        mock_request.files.get.return_value = None

        response = self.client.post(url_for('modify_lon.modify_lon_upload_post', charge_id="LLC-TST"))

        context_validation_error = self.get_context_variable('validation_errors')

        self.assert_status(response, 400)
        self.assertIsNotNone(context_validation_error["tribunal_definitive_certificate_date"])
        self.assertEqual(context_validation_error["tribunal_definitive_certificate_date"].inline_message,
                         "Check that the date is in Day/Month/Year format")

        self.assertIsNotNone(context_validation_error["definitive-certificate-file-input"])
        self.assertEqual(context_validation_error["definitive-certificate-file-input"].inline_message,
                         "Upload a document for Definitive Certificate")

    @patch('maintain_frontend.view_modify_lon.modify_lon.request')
    @patch('maintain_frontend.view_modify_lon.modify_lon.LocalLandChargeService')
    def test_vary_lon_validator_required_fields_form_b(self, mock_service, mock_request):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]
        self.mock_session.return_value.edited_fields = {}

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"item": get_mock_lon_item(), "display_id": "LLC-TST", "cancelled": False}]
        mock_service.return_value.get_by_charge_number.return_value = mock_response

        mock_request.form.getlist.return_value = ["Form B"]
        mock_request.files.get.return_value = None

        response = self.client.post(url_for('modify_lon.modify_lon_upload_post', charge_id="LLC-TST"))

        context_validation_error = self.get_context_variable('validation_errors')

        self.assert_status(response, 400)

        self.assertIsNotNone(context_validation_error["form-b-file-input"])
        self.assertEqual(context_validation_error["form-b-file-input"].inline_message,
                         "Upload a document for Form B")

    @patch('maintain_frontend.view_modify_lon.modify_lon.request')
    @patch('maintain_frontend.view_modify_lon.modify_lon.LocalLandChargeService')
    def test_vary_lon_validator_required_fields_court_order(self, mock_service, mock_request):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_lon]
        self.mock_session.return_value.edited_fields = {}

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"item": get_mock_lon_item(), "display_id": "LLC-TST", "cancelled": False}]
        mock_service.return_value.get_by_charge_number.return_value = mock_response

        mock_request.form.getlist.return_value = ["Court Order"]
        mock_request.files.get.return_value = None

        response = self.client.post(url_for('modify_lon.modify_lon_upload_post', charge_id="LLC-TST"))

        context_validation_error = self.get_context_variable('validation_errors')

        self.assert_status(response, 400)

        self.assertIsNotNone(context_validation_error["court-order-file-input"])
        self.assertEqual(context_validation_error["court-order-file-input"].inline_message,
                         "Upload a document for Court Order")
