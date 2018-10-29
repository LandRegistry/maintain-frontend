from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from unittest.mock import patch, MagicMock, call
from flask import url_for
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.services.charge_id_services import calc_display_id
import copy

local_land_charge_1 = {
    "geometry": {
        "type": "Point",
        "coordinates": [7, 8]
    },
    "registration-date": "2017-03-03",
    "charge-creation-date": "2004-01-04",
    "local-land-charge": 4,
    "charge-type": "Land compensation",
    "charge-geographic-description": "17 Main Street, Place",
    "further-information-location": "Council Offices, Water Dept.",
    "further-information-reference": "XR12433",
    "originating-authority": "Place City Council",
    "instrument": "Deed",
    "land-works-particulars": "The particulars of the land works",
    "land-sold-description": "The description of the land sold",
    "retained-land-description": "Description of the retained land",
    "start-date": "2015-01-01"
}

local_land_charge_2 = {
    "geometry": {
        "type": "Point",
        "coordinates": [7, 8]
    },
    "registration-date": "2017-03-03",
    "local-land-charge": 5,
    "charge-type": "Land compensation",
    "charge-geographic-description": "17 Main Street, Place",
    "further-information-location": "Council Offices, Water Dept.",
    "further-information-reference": "XR12433",
    "originating-authority": "Place City Council",
    "instrument": "Deed",
    "land-works-particulars": "The particulars of the land works",
    "land-sold-description": "The description of the land sold",
    "retained-land-description": "Description of the retained land",
    "start-date": "2015-01-01"
}


class TestModifyCharge(TestCase):

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    @patch('maintain_frontend.view_modify_land_charge.modify_land_charge.LocalAuthorityService')
    @patch('maintain_frontend.view_modify_land_charge.modify_land_charge.build_extents_from_features')
    @patch('maintain_frontend.view_modify_land_charge.modify_land_charge.LocalLandChargeService')
    def test_modify_get_invalid_id(self, mock_llc_service, mock_features, mock_la_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        mock_la_service.return_value.get_authorities_by_extent.return_value = ['test']

        response = self.client.get(url_for('modify_land_charge.modify_land_charge', local_land_charge=123))

        self.assert_status(response, 302)

    @patch('maintain_frontend.view_modify_land_charge.modify_land_charge.LocalAuthorityService')
    @patch('maintain_frontend.view_modify_land_charge.modify_land_charge.build_extents_from_features')
    @patch('maintain_frontend.view_modify_land_charge.modify_land_charge.LocalLandChargeService')
    def test_modify_get_found(self, mock_llc_service, mock_features, mock_la_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        self.mock_session.return_value.add_charge_state = None
        mock_response = MagicMock()
        mock_llc_service.return_value.get_by_charge_number.return_value = mock_response
        mock_response.status_code = 200
        mock_llc_service.return_value.get_history_for_charge.return_value = mock_response
        mock_response.status_code = 200

        mock_la_service.return_value.get_authorities_by_extent.return_value = ['test']

        lc_copy = copy.deepcopy(local_land_charge_1)

        mock_response.json.return_value = [{"item": lc_copy, "display_id": "LLC-TST", "cancelled": False}]
        response = self.client.get(url_for('modify_land_charge.modify_land_charge', local_land_charge='LLC-TST'))

        self.assert_status(response, 200)

    @patch('maintain_frontend.view_modify_land_charge.modify_land_charge.LocalAuthorityService')
    @patch('maintain_frontend.view_modify_land_charge.modify_land_charge.build_extents_from_features')
    @patch('maintain_frontend.view_modify_land_charge.modify_land_charge.LocalLandChargeService')
    def test_modify_get_not_found(self, mock_llc_service, mock_features, mock_la_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        mock_la_service.return_value.get_authorities_by_extent.return_value = ['test']

        self.mock_session.return_value.add_charge_state = None
        mock_response = MagicMock()
        mock_llc_service.return_value.get_by_charge_number.return_value = mock_response
        mock_response.status_code = 404
        response = self.client.get(url_for('modify_land_charge.modify_land_charge', local_land_charge='LLC-TST'))

        self.assert_status(response, 302)

    @patch('maintain_frontend.view_modify_land_charge.modify_land_charge.LocalAuthorityService')
    @patch('maintain_frontend.view_modify_land_charge.modify_land_charge.build_extents_from_features')
    @patch('maintain_frontend.view_modify_land_charge.modify_land_charge.LocalLandChargeService')
    def test_modify_redirect_when_different_id_in_session(self, mock_llc_service, mock_features, mock_la_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        mock_la_service.return_value.get_authorities_by_extent.return_value = ['test']

        state = LocalLandChargeItem.from_json(local_land_charge_1)
        self.mock_session.return_value.add_charge_state = state

        charge_id_from_url = 'LLC-98765'
        mock_response = MagicMock()
        mock_llc_service.return_value.get_by_charge_number.return_value = mock_response
        mock_response.status_code = 200
        mock_llc_service.return_value.get_history_for_charge.return_value = mock_response
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            "item": local_land_charge_2,
            "display_id": charge_id_from_url,
            "cancelled": False
        }]

        response = self.client.get(url_for(
            'modify_land_charge.modify_land_charge',
            local_land_charge=charge_id_from_url))

        self.assert_status(response, 200)
        mock_llc_service.return_value.get_by_charge_number.assert_called_with(charge_id_from_url)

    @patch('maintain_frontend.view_modify_land_charge.modify_land_charge.LocalAuthorityService')
    @patch('maintain_frontend.view_modify_land_charge.modify_land_charge.build_extents_from_features')
    @patch('maintain_frontend.view_modify_land_charge.modify_land_charge.LocalLandChargeService')
    def test_modify_get_cancelled(self, mock_llc_service, mock_features, mock_la_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        mock_la_service.return_value.get_authorities_by_extent.return_value = ['test']

        self.mock_session.return_value.add_charge_state = None
        s8_mod = copy.deepcopy(local_land_charge_1)
        s8_mod['end-date'] = "2012-12-12"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"item": s8_mod, "display_id": "LLC-TST", "cancelled": True}]

        mock_llc_service.return_value.get_by_charge_number.return_value = mock_response

        response = self.client.get(url_for('modify_land_charge.modify_land_charge', local_land_charge='LLC-TST'))

        self.assert_redirects(response, '/error')

    @patch('maintain_frontend.view_modify_land_charge.modify_land_charge.AuditAPIService')
    @patch('maintain_frontend.view_modify_land_charge.modify_land_charge.MaintainApiService')
    def test_modify_confirm_charge_outside_authority(self, mock_maintain_api_service, mock_audit):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        self.mock_session.return_value.user.organisation = 'test org'
        self.mock_session.return_value.charge_added_outside_users_authority = True
        self.mock_session.return_value.other_authority_update_permission = False

        state = LocalLandChargeItem.from_json(local_land_charge_1)
        self.mock_session.return_value.add_charge_state = state

        response = self.client.post(url_for('modify_land_charge.modify_land_charge_confirm'))

        self.assert_status(response, 200)
        self.assert_template_used('modify_confirmation.html')
        self.assert_context('charge_id', 'LLC-{}'.format(local_land_charge_1['local-land-charge']))
        expected_call = [
            call("Vary request submitted.",
                 supporting_info={'id': calc_display_id(local_land_charge_1['local-land-charge'])}),
            call("Charge location varied, extent(s) modified to be outside users authority.",
                 supporting_info={
                     'originating-authority': self.mock_session.return_value.user.organisation,
                     'id': calc_display_id(local_land_charge_1['local-land-charge'])
                 })
        ]

        mock_audit.audit_event.assert_has_calls(expected_call)

    @patch('maintain_frontend.view_modify_land_charge.modify_land_charge.AuditAPIService')
    @patch('maintain_frontend.view_modify_land_charge.modify_land_charge.MaintainApiService')
    def test_modify_confirm_other_authority_update_permission(self, mock_maintain_api_service, mock_audit):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        self.mock_session.return_value.user.organisation = 'test org'
        self.mock_session.return_value.charge_added_outside_users_authority = False
        self.mock_session.return_value.other_authority_update_permission = True

        state = LocalLandChargeItem.from_json(local_land_charge_1)
        self.mock_session.return_value.add_charge_state = state

        response = self.client.post(url_for('modify_land_charge.modify_land_charge_confirm'))

        self.assert_status(response, 200)
        self.assert_template_used('modify_confirmation.html')
        self.assert_context('charge_id', 'LLC-{}'.format(local_land_charge_1['local-land-charge']))
        expected_call = [
            call("Vary request submitted.",
                 supporting_info={'id': calc_display_id(local_land_charge_1['local-land-charge'])}),
            call("Charge location varied, extent(s) modified on a charge outside users authority.",
                 supporting_info={
                     'originating-authority': self.mock_session.return_value.user.organisation,
                     'id': calc_display_id(local_land_charge_1['local-land-charge'])
                 })
        ]

        mock_audit.audit_event.assert_has_calls(expected_call)

    @patch('maintain_frontend.view_modify_land_charge.modify_land_charge.AuditAPIService')
    @patch('maintain_frontend.view_modify_land_charge.modify_land_charge.MaintainApiService')
    def test_modify_confirm_charge_inside_authority(self, mock_maintain_api_service, mock_audit):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        self.mock_session.return_value.charge_added_outside_users_authority = False
        self.mock_session.return_value.other_authority_update_permission = False

        state = LocalLandChargeItem.from_json(local_land_charge_1)
        self.mock_session.return_value.add_charge_state = state

        response = self.client.post(url_for('modify_land_charge.modify_land_charge_confirm'))

        self.assert_status(response, 200)
        self.assert_template_used('modify_confirmation.html')
        self.assert_context('charge_id', 'LLC-{}'.format(local_land_charge_1['local-land-charge']))

        for calls in mock_audit.mock_calls:
            self.assertNotEqual(calls[1], "Charge location varied, extent(s) modified to be outside users authority.")

    def test_clear_land_charge_changes(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        self.mock_session.return_value.add_charge_state = {'add charge field': 'value'}
        self.mock_session.return_value.edited_fields = ['edited field']
        self.mock_session.return_value.charge_added_outside_users_authority = True

        response = self.client.get(url_for('modify_land_charge.clear_land_charge_changes', local_land_charge='1'))

        self.assert_status(response, 302)
        self.assertIsNone(self.mock_session.return_value.add_charge_state)
        self.assertEqual(self.mock_session.return_value.edited_fields, [])
        self.assertIsNone(self.mock_session.return_value.charge_added_outside_users_authority)
