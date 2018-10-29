from maintain_frontend.dependencies.maintain_api.maintain_api_service import MaintainApiService
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.services.charge_id_services import calc_display_id
from unittest import TestCase
from unittest.mock import patch, MagicMock
from maintain_frontend import main
from unit_tests.utilities import Utilities
from flask import g
from maintain_frontend.dependencies.session_api.user import User


MAINTAIN_API_NAME = 'maintain_frontend.dependencies.maintain_api.maintain_api_service'

s8 = {
    "geometry": {
        "type": "Point",
        "coordinates": [7, 8]
    },
    "registration-date": "2017-03-03",
    "local-land-charge": 4,
    "charge-type": "s8 Land Compensation Charge",
    "charge-geographic-description": "17 Main Street, Place",
    "further-information-location": "Council Offices, Water Dept.",
    "further-information-reference": "XR12433",
    "originating-authority": "Place City Council",
    "instrument": "Deed",
    "land-works-particulars": "The particulars of the land works",
    "retained-land-description": "Description of the retained land",
    "start-date": "2015-01-01"
}


class TestMaintainApiService(TestCase):

    def setUp(self):
        self.app = main.app.test_client()
        Utilities.mock_session_cookie_unittest(self)

    @patch('{}.current_app'.format(MAINTAIN_API_NAME))
    def test_post_add_land_charge_success(self, mock_app):
        with main.app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = '123'
            g.session = self.mock_session
            user = User()
            user.email = "abc"
            self.mock_session = user
            response = MagicMock()
            response.status_code = 202
            response.json.return_value = {"land_charge_id": "123",
                                          "entry_number": "1",
                                          "registration_date": "2000-01-01"}
            response.text = 'Success'
            g.requests.post.return_value = response

            MaintainApiService.add_charge(LocalLandChargeItem())

            self.assertIsNotNone(g.session.last_created_charge)
            self.assertEqual(g.session.last_created_charge.charge_id, "123")
            self.assertEqual(g.session.last_created_charge.registration_date, "01/01/2000")
            self.assertEqual(g.session.last_created_charge.entry_number, "1")
            self.assertEqual(g.requests.post.call_count, 1)

    @patch('{}.AuditAPIService'.format(MAINTAIN_API_NAME))
    @patch('{}.current_app'.format(MAINTAIN_API_NAME))
    def test_post_add_land_charge_exception(self, mock_app, mock_audit):
        with main.app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = '123'
            g.session = self.mock_session
            response = MagicMock()
            response.status_code = 500
            response.text = "response"
            g.requests.post.side_effect = Exception('test exception')
            g.requests.post.return_value = response
            land_charge = LocalLandChargeItem()
            land_charge.local_land_charge = '1'

            try:
                MaintainApiService.add_charge(land_charge)
            except Exception as ex:
                self.assertEqual(ex.http_code, 500)
                mock_app.logger.exception.assert_called()
                mock_app.logger.exception.assert_called_with(
                    'Failed to send land charge to maintain-api. TraceID : 123 - Exception - test exception')
                mock_audit.audit_event.assert_called_with('Failed to send land charge to maintain-api')
                return
            self.fail()

    @patch('{}.AuditAPIService'.format(MAINTAIN_API_NAME))
    @patch('{}.current_app'.format(MAINTAIN_API_NAME))
    def test_post_add_land_charge_validation_error(self, mock_app, mock_audit):
        with main.app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = '123'
            g.session = self.mock_session
            response = MagicMock()
            response.status_code = 500
            response.text = "response"
            g.requests.post.return_value = response
            land_charge = LocalLandChargeItem()
            land_charge.local_land_charge = '1'

            try:
                MaintainApiService.add_charge(land_charge)
            except Exception as ex:
                self.assertEqual(ex.http_code, 500)
                mock_app.logger.exception.assert_called()
                mock_app.logger.exception.assert_called_with(
                    'Failed to send land charge to maintain-api. TraceID : 123 - Status: 500, Message: response')
                mock_audit.audit_event.assert_called_with('Failed to send land charge to maintain-api')
                return
            self.fail()

    @patch('{}.current_app'.format(MAINTAIN_API_NAME))
    def test_put_update_land_charge_success(self, mock_app):
        with main.app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = '123'
            g.session = self.mock_session
            user = User()
            user.username = "abc"
            self.mock_session = user
            response = MagicMock()
            response.status_code = 202
            response.json.return_value = {
                "entry_number": "1", "land_charge_id": "4", "registration_date": "2012-12-12"
            }
            response.text = 'Success'
            g.requests.put.return_value = response

            MaintainApiService.update_charge(LocalLandChargeItem.from_json(s8))

            self.assertIsNotNone(g.session.last_created_charge)
            self.assertEqual(g.session.last_created_charge.charge_id, "4")
            self.assertEqual(g.session.last_created_charge.registration_date, "12/12/2012")
            self.assertEqual(g.session.last_created_charge.entry_number, "1")
            self.assertEqual(g.requests.put.call_count, 1)

    @patch('{}.AuditAPIService'.format(MAINTAIN_API_NAME))
    @patch('{}.current_app'.format(MAINTAIN_API_NAME))
    def test_put_update_land_charge_exception(self, mock_app, mock_audit):
        with main.app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = '123'
            g.session = self.mock_session
            response = MagicMock()
            response.status_code = 500
            response.text = "response"
            g.requests.put.side_effect = Exception('test exception')
            g.requests.put.return_value = response

            try:
                MaintainApiService.update_charge(LocalLandChargeItem.from_json(s8))
            except Exception as ex:
                self.assertEqual(ex.http_code, 500)
                mock_app.logger.exception.assert_called()
                mock_app.logger.exception.assert_called_with(
                    'Failed to send land charge to maintain-api. TraceID : 123 - Exception - test exception')
                mock_audit.audit_event.assert_called_with('Failed to send land charge to maintain-api',
                                                          supporting_info={
                                                              'id': calc_display_id(s8['local-land-charge'])
                                                          })
                return
            self.fail()

    @patch('{}.AuditAPIService'.format(MAINTAIN_API_NAME))
    @patch('{}.current_app'.format(MAINTAIN_API_NAME))
    def test_put_update_land_charge_validation_error(self, mock_app, mock_audit):
        with main.app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = '123'
            g.session = self.mock_session
            response = MagicMock()
            response.status_code = 500
            response.text = "response"
            g.requests.put.return_value = response

            try:
                MaintainApiService.update_charge(LocalLandChargeItem.from_json(s8))
            except Exception as ex:
                self.assertEqual(ex.http_code, 500)
                mock_app.logger.exception.assert_called()
                mock_app.logger.exception.assert_called_with(
                    'Failed to send land charge to maintain-api. TraceID : 123 - Status: 500, Message: response')
                mock_audit.audit_event.assert_called_with('Failed to send land charge to maintain-api',
                                                          supporting_info={
                                                              'id': calc_display_id(s8['local-land-charge'])
                                                          })
                return
            self.fail()
