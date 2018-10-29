from unittest import TestCase
from unittest.mock import MagicMock
from maintain_frontend.add_land_charge.routing.review_router import ReviewRouter
from maintain_frontend import main
from flask import g
from maintain_frontend.models import LocalLandChargeItem

REDIRECT_ROUTE = 'add_land_charge.get_charge_description'
REDIRECT_URL = '/add-local-land-charge/charge-description'

DEFAULT_ROUTE = 'add_land_charge.get_charge_date'
DEFAULT_URL = '/add-local-land-charge/when-was-charge-created'

CHARGE_TYPE = 'some charge type'


class TestReviewRouter(TestCase):

    def test_get_redirect_url_with_redirect_route_set(self):
        """Should return the URL of the redirect_route if the redirect_route is set in session."""
        with main.app.test_request_context():
            self.build_session()
            g.session.redirect_route = REDIRECT_ROUTE

            result = ReviewRouter.get_redirect_url(DEFAULT_ROUTE)
            self.assertEqual(result, REDIRECT_URL)

    def test_get_redirect_url_with_redirect_route_not_set(self):
        """Should return the URL of the given route if the redirect_route is not set in session."""
        with main.app.test_request_context():
            self.build_session()
            g.session.redirect_route = None

            result = ReviewRouter.get_redirect_url(DEFAULT_ROUTE)
            self.assertEqual(result, DEFAULT_URL)

    def test_update_edited_field_with_redirect_route_set_and_pass_matching_field(self):
        """Should not add an entry to the edited_fields if the given value matches the value stored in session."""
        with main.app.test_request_context():
            self.build_session()
            g.session.add_charge_state.charge_type = CHARGE_TYPE
            g.session.redirect_route = REDIRECT_ROUTE

            ReviewRouter.update_edited_field('charge_type', CHARGE_TYPE)
            self.assertTrue(len(g.session.edited_fields) == 0)

    def test_update_edited_field_with_redirect_route_set_and_pass_non_matching_field(self):
        """Should add an entry to the edited_fields if the given value does not match the value stored in session."""
        with main.app.test_request_context():
            self.build_session()
            g.session.redirect_route = REDIRECT_ROUTE

            ReviewRouter.update_edited_field('charge_type', CHARGE_TYPE)
            self.assertTrue(len(g.session.edited_fields) == 1)
            self.assertIn('charge_type', g.session.edited_fields)

    def test_update_edited_field_with_redirect_route_not_set(self):
        """Should not update edited_fields if the redirect_route in session is not set."""
        with main.app.test_request_context():
            self.build_session()
            g.session.add_charge_state.charge_type = CHARGE_TYPE
            g.session.redirect_route = None

            ReviewRouter.update_edited_field('charge_type', CHARGE_TYPE)
            self.assertTrue(len(g.session.edited_fields) == 0)

    @staticmethod
    def build_session():
        g.session = MagicMock()
        g.session.add_charge_state = LocalLandChargeItem()
        g.session.edited_fields = []
        g.trace_id = 'some trace id'
