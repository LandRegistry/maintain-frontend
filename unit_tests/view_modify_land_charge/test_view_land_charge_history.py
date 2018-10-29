from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from unittest.mock import patch, MagicMock
from flask import url_for
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.view_modify_land_charge.view_land_charge_history import history_change_overview_format

local_land_charge_history_item = {
    "cancelled": "false",
    "item-changes": {
        "further-information-location": {"old": "Test", "new": "Test"},
        "further-information-reference": {"old": "Test", "new": "Test"},
        "expiry-date": {"old": "Test", "new": "Test"},
        "charge-creation-date": {"old": "Test", "new": "Test"},
        "charge-geographic-description": {"old": "Test", "new": "Test"},
        "statutory-provision": {"old": "Test", "new": "Test"},
        "geometry": {"old": "Test", "new": "Test"},
        "madeup-field": {"old": "Test", "new": "Test"},
        "supplementary-information": {"old": "Test", "new": "Test"}
    },
    "entry-timestamp": "2016-04-28 13:44:53"
}


lon_history_item = {
    "cancelled": "false",
    "item-changes": {
        "applicant-name": {"old": "Test", "new": "Test"},
        "applicant-address": {"old": "Test", "new": "Test"},
        "further-information-location": {"old": "Test", "new": "Test"},
        "further-information-reference": {"old": "Test", "new": "Test"},
        "expiry-date": {"old": "Test", "new": "Test"},
        "charge-creation-date": {"old": "Test", "new": "Test"},
        "charge-geographic-description": {"old": "Test", "new": "Test"},
        "documents-filed": {"old": "Test", "new": "Test"},
        "statutory-provision": {"old": "Test", "new": "Test"},
        "geometry": {"old": "Test", "new": "Test"},
        "structure-position-and-dimension": {"old": "Test", "new": "Test"},
        "servient-land-interest-description": {"old": "Test", "new": "Test"},
        "tribunal-temporary-certificate-expiry-date": {"old": "Test", "new": "Test"},
        "tribunal-definitive-certificate-date": {"old": "Test", "new": "Test"},
        "tribunal-temporary-certificate-date": {"old": "Test", "new": "Test"},
        "madeup-field": {"old": "Test", "new": "Test"}
    },
    "entry-timestamp": "2016-04-28 13:44:53"
}


class TestViewChargeHistory(TestCase):

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    @patch('maintain_frontend.view_modify_land_charge.view_land_charge_history.LocalLandChargeService')
    def test_view_history_invalid_id(self, mock_llc_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.retrieve_llc]

        response = self.client.get(url_for('view_land_charge.history', charge_id=123))

        self.assert_status(response, 302)

    @patch('maintain_frontend.view_modify_land_charge.view_land_charge_history.LocalLandChargeService')
    @patch('maintain_frontend.view_modify_land_charge.view_land_charge_history.LocalLandChargeHistoryItem')
    def test_view_history_found(self, mock_model, mock_llc_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.retrieve_llc]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"item-changes": {}, "cancelled": False}]

        mock_llc_service.return_value.get_history_for_charge.return_value = mock_response

        response = self.client.get(url_for('view_land_charge.history', charge_id='LLC-TST'))

        self.assert_status(response, 200)

    @patch('maintain_frontend.view_modify_land_charge.view_land_charge_history.LocalLandChargeService')
    def test_view_not_found(self, mock_llc_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.retrieve_llc]

        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_llc_service.return_value.get_history_for_charge.return_value = mock_response

        response = self.client.get(url_for('view_land_charge.history', charge_id='LLC-TST'))

        self.assert_status(response, 302)

    @patch('maintain_frontend.view_modify_land_charge.view_land_charge_history.LocalLandChargeService')
    def test_search_api_result_not_found(self, mock_llc_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.retrieve_llc]

        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_llc_service.return_value.get_by_charge_number.return_value = mock_response

        response = self.client.get(url_for('view_land_charge.history', charge_id='LLC-TST'))

        self.assert_status(response, 302)

    @patch('maintain_frontend.view_modify_land_charge.view_land_charge_history.LocalLandChargeService')
    def test_search_and_history_not_found(self, mock_llc_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.retrieve_llc]

        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_llc_service.return_value.get_by_charge_number.return_value = mock_response
        mock_llc_service.return_value.get_by_charge_number.return_value = mock_response

        response = self.client.get(url_for('view_land_charge.history', charge_id='LLC-TST'))

        self.assert_status(response, 302)

    @patch('maintain_frontend.view_modify_land_charge.view_land_charge_history.LocalLandChargeService')
    def test_search_and_history_500_response(self, mock_llc_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.retrieve_llc]

        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_llc_service.return_value.get_by_charge_number.return_value = mock_response
        mock_llc_service.return_value.get_by_charge_number.return_value = mock_response

        response = self.client.get(url_for('view_land_charge.history', charge_id='LLC-TST'))

        self.assert_status(response, 302)

    @patch('maintain_frontend.view_modify_land_charge.view_land_charge_history.LocalLandChargeService')
    def test_search_for_charge_500_response(self, mock_llc_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.retrieve_llc]

        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_llc_service.return_value.get_by_charge_number.return_value = mock_response

        response = self.client.get(url_for('view_land_charge.history', charge_id='LLC-TST'))

        self.assert_status(response, 302)

    @patch('maintain_frontend.view_modify_land_charge.view_land_charge_history.LocalLandChargeService')
    def test_charge_history_500_response(self, mock_llc_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.retrieve_llc]

        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_llc_service.return_value.get_by_charge_number.return_value = mock_response

        response = self.client.get(url_for('view_land_charge.history', charge_id='LLC-TST'))

        self.assert_status(response, 302)

    def test_view_history_formatting_valid(self,):
        history = MagicMock()
        history.cancelled = False
        history.item_changes = local_land_charge_history_item['item-changes']

        changes = history_change_overview_format(history)
        self.assertIn("Expiry date", changes)
        self.assertIn("Law", changes)
        self.assertIn("Description", changes)
        self.assertIn("Authority reference", changes)
        self.assertIn("Extent", changes)
        self.assertIn("Creation date", changes)
        self.assertIn("Location", changes)
        self.assertIn("Madeup Field", changes)
        self.assertIn("Source information", changes)

    def test_view_lon_history_formatting_valid(self,):
        history = MagicMock()
        history.cancelled = False
        history.item_changes = lon_history_item['item-changes']

        changes = history_change_overview_format(history, "Light obstruction notice")
        self.assertIn("Expiry date", changes)
        self.assertIn("Temporary expiry date", changes)
        self.assertIn("Temporary certificate date", changes)
        self.assertIn("Definitive certificate date", changes)
        self.assertIn("Address: person applying for the light obstruction notice", changes)
        self.assertIn("Name: person applying for the light obstruction notice", changes)
        self.assertIn("Legal Document(s)", changes)
        self.assertIn("Law", changes)
        self.assertIn("Source information", changes)
        self.assertIn("Authority reference", changes)
        self.assertIn("Extent", changes)
        self.assertIn("Creation date", changes)
        self.assertIn("Address - Dominant building", changes)
        self.assertIn("Madeup Field", changes)
        self.assertIn("Interest in the land", changes)
        self.assertIn("Height and extent: Planned development", changes)

    def test_view_history_formatting_cancelled(self,):
        history = MagicMock()
        history.cancelled = True

        changes = history_change_overview_format(history)
        self.assertIn("Charge is cancelled", changes)

    def test_view_history_author_removed(self,):
        history = MagicMock()
        history.cancelled = False
        history.item_changes = {"author": {"old": "J R Hartley", "new": "Douglas Adams"},
                                "expiry-date": {"old": "Test", "new": "Test"}}

        changes = history_change_overview_format(history)

        self.assertNotIn("Author", changes)
        self.assertIn("Expiry", changes)

    def test_view_history_author_removed_empty(self,):
        history = MagicMock()
        history.cancelled = False
        history.item_changes = {"author": {"old": "J R Hartley", "new": "Douglas Adams"}}

        changes = history_change_overview_format(history)

        self.assertEqual(changes, "No changes made")
