from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from unittest.mock import patch, MagicMock
from flask import url_for
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.view_modify_land_charge.view_land_charge import get_history_update_info_by_charge_id
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
    "further-information-location": "Council Offices, Water Dept.",
    "further-information-reference": "XR12433",
    "originating-authority": "Place City Council",
    "instrument": "Deed",
    "land-works-particulars": "The particulars of the land works",
    "land-sold-description": "The description of the land sold",
    "retained-land-description": "Description of the retained land",
    "start-date": "2015-01-01"
}

history_list = [{
    "entry-timestamp": "2017-06-08T10:13:32",
    "author": {
        "organisation": "LR test",
        "email": "test@test.com",
        "full-name": "test"
    },
    "cancelled": False
},
    {"item-changes": {
        "charge-geographic-description":
        {"old": "more info text", "new": "more info text change 1"}
    },
    "entry-timestamp": "2017-06-08T10:38:27",
    "author": {
        "organisation": "LR test",
        "email": "test@test.com",
        "full-name": "test"
    },
    "cancelled": False
},
    {"item-changes": {
        "end-date": {"old": "", "new": "2017-06-12"}
    },
    "entry-timestamp": "2017-06-12T11:20:01",
    "author": {
        "organisation": "LR test",
        "email": "test@test.com",
        "full-name": "test"},
        "cancelled": True
}
]


class TestViewCharge(TestCase):

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    @patch('maintain_frontend.view_modify_land_charge.view_land_charge.LocalLandChargeService')
    def test_view_invalid_id(self, mock_llcservice):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.retrieve_llc]

        response = self.client.get(url_for('view_land_charge.view_land_charge', local_land_charge=123))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/page-not-found')

    @patch('maintain_frontend.view_modify_land_charge.view_land_charge.AuditAPIService')
    @patch('maintain_frontend.view_modify_land_charge.view_land_charge.LocalLandChargeService')
    def test_view_found(self, mock_llcservice, mock_audit):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.retrieve_llc]

        s8_copy = copy.deepcopy(s8)
        mock_response = MagicMock()
        mock_llcservice.return_value.get_by_charge_number.return_value = mock_response
        mock_response.status_code = 200
        mock_response.json.return_value = [{"item": s8_copy, "display_id": "LLC-TST", "cancelled": False}]
        response = self.client.get(url_for('view_land_charge.view_land_charge', local_land_charge='LLC-TST'))

        self.assert_status(response, 200)

    @patch('maintain_frontend.view_modify_land_charge.view_land_charge.LocalLandChargeService')
    def test_view_not_found(self, mock_llcservice):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.retrieve_llc]

        mock_response = MagicMock()
        mock_llcservice.return_value.get_by_charge_number.return_value = mock_response
        mock_response.status_code = 404
        response = self.client.get(url_for('view_land_charge.view_land_charge', local_land_charge='LLC-TST'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/page-not-found')

    @patch('maintain_frontend.view_modify_land_charge.view_land_charge.AuditAPIService')
    @patch('maintain_frontend.view_modify_land_charge.view_land_charge.LocalLandChargeService')
    def test_view_cancelled(self, mock_llcservice, mock_audit):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.retrieve_llc]

        mock_response = MagicMock()
        mock_llcservice.return_value.get_by_charge_number.return_value = mock_response
        mock_response.status_code = 200
        s8_mod = copy.deepcopy(s8)
        s8_mod['end-date'] = "2012-12-12"
        mock_response.json.return_value = [{"item": s8_mod, "display_id": "LLC-TST", "cancelled": True}]
        response = self.client.get(url_for('view_land_charge.view_land_charge', local_land_charge='LLC-TST'))

        self.assert_status(response, 200)

    @patch('maintain_frontend.view_modify_land_charge.view_land_charge.AuditAPIService')
    @patch('maintain_frontend.view_modify_land_charge.view_land_charge.LocalLandChargeService')
    def test_format_dates(self, mock_llcservice, mock_audit):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.retrieve_llc]

        mock_response = MagicMock()
        mock_llcservice.return_value.get_by_charge_number.return_value = mock_response
        mock_response.status_code = 200
        s8_mod = copy.deepcopy(s8)
        s8_mod['end-date'] = "2012-12-12"
        s8_mod['charge-creation-date'] = "2012-01-01"
        s8_mod['expiry-date'] = "2012-11-30"
        mock_response.json.return_value = [{"item": s8_mod, "display_id": "LLC-TST", "cancelled": True}]
        response = self.client.get(url_for('view_land_charge.view_land_charge', local_land_charge='LLC-TST'))

        self.assert_status(response, 200)
        self.assertEqual(self.get_context_variable('charge_item').end_date.strftime('%-d %B %Y'), '12 December 2012')
        self.assertEqual(self.get_context_variable('charge_item').charge_creation_date.strftime('%-d %B %Y'),
                         '1 January 2012')
        self.assertEqual(self.get_context_variable('charge_item').expiry_date.strftime('%-d %B %Y'),
                         '30 November 2012')

    @patch('maintain_frontend.view_modify_land_charge.view_land_charge.LocalLandChargeService')
    def test_land_charge_history_not_found(self, mock_llcservice):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.retrieve_llc]

        s8_copy = copy.deepcopy(s8)
        mock_charge_response = MagicMock()
        mock_charge_response.status_code = 200
        mock_charge_response.json.return_value = [{"item": s8_copy, "display_id": "LLC-TST", "cancelled": False}]
        mock_llcservice.return_value.get_by_charge_number.return_value = mock_charge_response

        mock_history_response = MagicMock()
        mock_history_response.status_code = 404
        mock_llcservice.return_value.get_history_for_charge.return_value = mock_history_response

        response = self.client.get(url_for('view_land_charge.view_land_charge', local_land_charge='LLC-TST'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/page-not-found')

    @patch('maintain_frontend.view_modify_land_charge.view_land_charge.LocalLandChargeService')
    def test_check_history_more_than_one(self, mock_llcservice):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.retrieve_llc]

        mock_response = MagicMock()
        mock_llcservice.get_history_for_charge.return_value = mock_response
        mock_response.status_code = 200
        mock_response.json.return_value = history_list

        a, b = get_history_update_info_by_charge_id("LLC-TST", mock_llcservice)
        assert a is True
        assert b == "12 June 2017"

    @patch('maintain_frontend.view_modify_land_charge.view_land_charge.LocalLandChargeService')
    def test_check_history_only_one(self, mock_llcservice):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.retrieve_llc]

        mock_response = MagicMock()
        mock_llcservice.get_history_for_charge.return_value = mock_response
        mock_response.status_code = 200
        single_history = [history_list[0]]
        mock_response.json.return_value = single_history

        a, b = get_history_update_info_by_charge_id("LLC-TST", mock_llcservice)
        assert a is False
        assert b is None
