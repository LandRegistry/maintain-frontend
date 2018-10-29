from maintain_frontend import main
from maintain_frontend.exceptions import ApplicationError
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from unittest.mock import patch, MagicMock, call
from flask import url_for
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.constants.permissions import Permissions
import copy

s8 = {
    "geometry": {
        "type": "Point",
        "coordinates": [7, 8]
    },
    "registration-date": "2017-03-03",
    "local-land-charge": 4,
    "charge-type": "Land compensation",
    "charge-geographic-description": "17 Main Street, Place",
    "further-information": [
        {
            "information-location": "Council Offices, Water Dept.",
            "references": ["XR12433", "XA000998"]
        }
    ],
    "originating-authority": "Place City Council",
    "instrument": "Deed",
    "land-works-particulars": "The particulars of the land works",
    "land-sold-description": "The description of the land sold",
    "retained-land-description": "Description of the retained land",
    "start-date": "2015-01-01"
}


class TestCancelCharge(TestCase):

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    @patch('maintain_frontend.view_modify_land_charge.cancel_land_charge.LocalLandChargeService')
    def test_cancel_get_not_found(self, mock_llcservice):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.cancel_llc]
        mock_response = MagicMock()
        mock_llcservice.return_value.get_by_charge_number.return_value = mock_response
        mock_response.status_code = 404

        response = self.client.get(url_for('cancel_land_charge.cancel_charge', charge_id='LLC-TST'))

        self.assert_status(response, 302)

    @patch('maintain_frontend.view_modify_land_charge.cancel_land_charge.build_extents_from_features')
    @patch('maintain_frontend.view_modify_land_charge.cancel_land_charge.LocalAuthorityService')
    @patch('maintain_frontend.view_modify_land_charge.cancel_land_charge.LocalLandChargeService')
    def test_cancel_get_found(self, mock_llcservice, mock_laservice, mock_buildextents):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.cancel_llc]

        s8_copy = copy.deepcopy(s8)
        mock_response = MagicMock()
        mock_llcservice.return_value.get_by_charge_number.return_value = mock_response
        mock_laservice.return_value.get_authorities_by_extent.return_value = ['test']
        mock_response.status_code = 200
        mock_response.json.return_value = [{"item": s8_copy, "display_id": "LLC-TST"}]

        response = self.client.get(url_for('cancel_land_charge.cancel_charge', charge_id='LLC-TST'))

        self.assert_status(response, 200)

    @patch('maintain_frontend.view_modify_land_charge.cancel_land_charge.LocalLandChargeService')
    @patch('maintain_frontend.view_modify_land_charge.cancel_land_charge.MaintainApiService')
    def test_cancel_post_fail(self, mock_maintain, mock_llcservice):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.cancel_llc]
        mock_response = MagicMock()
        mock_llcservice.return_value.get_by_charge_number.return_value = mock_response
        mock_response.status_code = 200
        mock_response.json.return_value = [{"item": {"actual_charge": s8}, "display_id": "LLC-TST"}]
        mock_maintain.update_charge.side_effect = ApplicationError(500)
        response = self.client.post(url_for('cancel_land_charge.cancel_charge', charge_id='LLC-TST'))

        self.assert_status(response, 302)

    @patch('maintain_frontend.view_modify_land_charge.cancel_land_charge.AuditAPIService')
    @patch('maintain_frontend.view_modify_land_charge.cancel_land_charge.LocalLandChargeService')
    @patch('maintain_frontend.view_modify_land_charge.cancel_land_charge.MaintainApiService')
    def test_cancel_post_found(self, mock_maintain, mock_llcservice, mock_audit):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.cancel_llc]

        s8_copy = copy.deepcopy(s8)
        mock_response = MagicMock()
        mock_llcservice.return_value.get_by_charge_number.return_value = mock_response
        mock_response.status_code = 200
        mock_response.json.return_value = [{"item": s8_copy, "display_id": "LLC-TST"}]
        mock_response2 = MagicMock()
        mock_maintain.update_charge.return_value = mock_response2
        mock_response2.status_code = 200
        response = self.client.post(url_for('cancel_land_charge.cancel_charge', charge_id='LLC-TST'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('cancel_land_charge.cancel_confirmation', charge_id='LLC-TST'))

        expected_calls = [
            call('Cancelling charge', supporting_info={'id': 'LLC-TST'})
        ]
        mock_audit.audit_event.assert_has_calls(expected_calls)
