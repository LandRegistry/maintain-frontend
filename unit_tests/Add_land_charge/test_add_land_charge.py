from maintain_frontend import main, config
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from flask import url_for
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LocalLandChargeItem


class TestNewCharge(TestCase):

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def test_add_new(self):
        """Should reset the session values and redirect to the get_charge_type page."""
        self.client.set_cookie(
            'localhost', Session.session_cookie_name, 'cookie_value')

        response = self.client.get(url_for('add_land_charge.new'))

        self.assertTrue(isinstance(
            self.mock_session.return_value.add_charge_state, LocalLandChargeItem))
        self.assertIsNone(self.mock_session.return_value.redirect_route)
        self.assertEqual(self.mock_session.return_value.edited_fields, [])
        self.assertFalse(
            self.mock_session.return_value.adding_charge_for_other_authority)
        self.assertEqual(
            self.mock_session.return_value.add_charge_state.originating_authority,
            self.mock_session.return_value.user.organisation
        )
        self.assertEqual(
            self.mock_session.return_value.add_charge_state.schema_version, config.SCHEMA_VERSION)
        self.assertIsNone(
            self.mock_session.return_value.upload_shapefile_processed)
        self.assertIsNone(self.mock_session.return_value.category_details)
        self.assertIsNone(self.mock_session.return_value.category_confirmation)
        self.assertIsNone(
            self.mock_session.return_value.charge_added_outside_users_authority)
        self.assertIsNone(
            self.mock_session.return_value.other_authority_update_permission)
        self.assertIsNone(
            self.mock_session.return_value.other_authority_cancel_permission)

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for(
            'add_land_charge.get_charge_type'))
        self.mock_session.return_value.commit.assert_called()

    def test_new_behalf_of_authority(self):
        """Should reset the session values and redirect to the get_charge_type page."""
        self.client.set_cookie(
            'localhost', Session.session_cookie_name, 'cookie_value')

        response = self.client.get(
            url_for('add_land_charge.new_behalf_of_authority'))

        self.assertTrue(isinstance(
            self.mock_session.return_value.add_charge_state, LocalLandChargeItem))
        self.assertIsNone(self.mock_session.return_value.redirect_route)
        self.assertEqual(self.mock_session.return_value.edited_fields, [])
        self.assertTrue(
            self.mock_session.return_value.adding_charge_for_other_authority)
        self.assertEqual(
            self.mock_session.return_value.add_charge_state.schema_version, config.SCHEMA_VERSION)
        self.assertIsNone(
            self.mock_session.return_value.upload_shapefile_processed)
        self.assertIsNone(self.mock_session.return_value.category_details)
        self.assertIsNone(self.mock_session.return_value.category_confirmation)
        self.assertIsNone(
            self.mock_session.return_value.charge_added_outside_users_authority)
        self.assertIsNone(
            self.mock_session.return_value.other_authority_update_permission)
        self.assertIsNone(
            self.mock_session.return_value.other_authority_cancel_permission)

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for(
            'add_land_charge.get_originating_authority_page'))
        self.mock_session.return_value.commit.assert_called()
