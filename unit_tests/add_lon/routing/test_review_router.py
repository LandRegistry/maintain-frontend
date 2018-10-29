from unittest import TestCase
from unittest.mock import MagicMock
from maintain_frontend.add_lon.routing.review_router import ReviewRouter
from maintain_frontend import main
from flask import g
from maintain_frontend.models import LightObstructionNoticeItem

REDIRECT_ROUTE = 'add_land_charge.get_charge_description'
REDIRECT_URL = '/add-local-land-charge/charge-description'

DEFAULT_ROUTE = 'add_land_charge.get_charge_date'
DEFAULT_URL = '/add-local-land-charge/when-was-charge-created'

CHARGE_TYPE = 'some charge type'
CHARGE_GEOGRAPHIC_DESCRIPTION = 'some geographic description'
CHARGE_ADDRESS = 'some charge address'


class TestReviewRouter(TestCase):

    def test_get_redirect_url(self):
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

    def test_update_edited_field_with_matching_field(self):
        """Should not add an entry to the edited_fields if the given value matches the value stored in session."""
        with main.app.test_request_context():
            self.build_session()
            g.session.add_lon_charge_state.charge_type = CHARGE_TYPE
            g.session.redirect_route = REDIRECT_ROUTE

            ReviewRouter.update_edited_field('charge_type', CHARGE_TYPE)
            self.assertTrue(len(g.session.edited_fields) == 0)

    def test_update_edited_field_with_different_field(self):
        """Should not add an entry to the edited_fields if the given value matches the value stored in session."""
        with main.app.test_request_context():
            self.build_session()
            g.session.add_lon_charge_state.charge_type = CHARGE_TYPE
            g.session.redirect_route = REDIRECT_ROUTE

            ReviewRouter.update_edited_field('charge_type', 'new charge type')
            self.assertTrue(len(g.session.edited_fields) == 1)
            self.assertIn('charge_type', g.session.edited_fields)

    def test_update_edited_field_with_empty_session(self):
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
            g.session.add_lon_charge_state.charge_type = CHARGE_TYPE
            g.session.redirect_route = None

            ReviewRouter.update_edited_field('charge_type', CHARGE_TYPE)
            self.assertTrue(len(g.session.edited_fields) == 0)

    def test_update_edited_dominant_address_with_redirect_route_not_set(self):
        """Should not update edited_fields if the redirect_route in session is not set."""
        with main.app.test_request_context():
            self.build_session()
            g.session.add_lon_charge_state.charge_geographic_description = CHARGE_GEOGRAPHIC_DESCRIPTION
            g.session.redirect_route = None

            ReviewRouter.update_edited_dominant_address('charge_geographic_description', CHARGE_GEOGRAPHIC_DESCRIPTION)
            self.assertTrue(len(g.session.edited_fields) == 0)

    def test_update_edited_dominant_address_with_old_address_new_description(self):
        """Should remove charge address if charge geo description is changed."""
        with main.app.test_request_context():
            self.build_session()
            g.session.add_lon_charge_state.charge_geographic_description = CHARGE_GEOGRAPHIC_DESCRIPTION
            g.session.redirect_route = REDIRECT_ROUTE
            g.session.edited_fields = {'charge_address': 'charge_address'}

            ReviewRouter.update_edited_dominant_address('charge_geographic_description', 'new geographic description')
            self.assertTrue(len(g.session.edited_fields) == 1)
            self.assertIn('charge_geographic_description', g.session.edited_fields)
            self.assertNotIn('charge_address', g.session.edited_fields)

    def test_update_edited_dominant_address_with_old_description_new_address(self):
        """Should remove charge geo description if charge address is changed."""
        with main.app.test_request_context():
            self.build_session()
            g.session.add_lon_charge_state.charge_geographic_description = CHARGE_GEOGRAPHIC_DESCRIPTION
            g.session.redirect_route = REDIRECT_ROUTE
            g.session.edited_fields = {'charge_geographic_description': 'charge_geographic_description'}

            ReviewRouter.update_edited_dominant_address('charge_address', 'new address')
            self.assertTrue(len(g.session.edited_fields) == 1)
            self.assertIn('charge_address', g.session.edited_fields)
            self.assertNotIn('charge_geographic_description', g.session.edited_fields)

    def test_update_update_edited_height_or_position_with_redirect_route_not_set(self):
        with main.app.test_request_context():
            self.build_session()
            g.session.add_lon_charge_state.structure_position_and_dimension = {}
            g.session.redirect_route = None

            ReviewRouter.update_edited_height_or_position({})
            self.assertTrue(len(g.session.edited_fields) == 0)

    def test_update_update_edited_height_or_position_change_height_type(self):
        with main.app.test_request_context():
            self.build_session()
            g.session.add_lon_charge_state.structure_position_and_dimension = {'height': 'unlimited height',
                                                                               'extent-covered': 'all of the extent'}
            g.session.redirect_route = REDIRECT_ROUTE

            ReviewRouter.update_edited_height_or_position({'height': '10', 'units': 'metres',
                                                           'extent-covered': 'all of the extent'})
            self.assertTrue(len(g.session.edited_fields) == 1)
            self.assertIn('servient_height', g.session.edited_fields)

    def test_update_update_edited_height_or_position_change_height_value(self):
        with main.app.test_request_context():
            self.build_session()
            g.session.add_lon_charge_state.structure_position_and_dimension = {'height': '10', 'units': 'metres',
                                                                               'extent-covered': 'all of the extent'}
            g.session.redirect_route = REDIRECT_ROUTE

            ReviewRouter.update_edited_height_or_position({'height': '20', 'units': 'metres',
                                                           'extent-covered': 'all of the extent'})
            self.assertTrue(len(g.session.edited_fields) == 1)
            self.assertIn('servient_height', g.session.edited_fields)

    def test_update_update_edited_height_or_position_change_units(self):
        with main.app.test_request_context():
            self.build_session()
            g.session.add_lon_charge_state.structure_position_and_dimension = {'height': '10', 'units': 'metres',
                                                                               'extent-covered': 'all of the extent'}
            g.session.redirect_route = REDIRECT_ROUTE

            ReviewRouter.update_edited_height_or_position({'height': '10', 'units': 'feet',
                                                           'extent-covered': 'all of the extent'})
            self.assertEqual(len(g.session.edited_fields), 1)
            self.assertIn('servient_height', g.session.edited_fields)

    def test_update_update_edited_height_or_position_change_height_and_units(self):
        with main.app.test_request_context():
            self.build_session()
            g.session.add_lon_charge_state.structure_position_and_dimension = {'height': '10', 'units': 'metres',
                                                                               'extent-covered': 'all of the extent'}
            g.session.redirect_route = REDIRECT_ROUTE

            ReviewRouter.update_edited_height_or_position({'height': '20', 'units': 'feet',
                                                           'extent-covered': 'all of the extent'})
            self.assertTrue(len(g.session.edited_fields) == 1)
            self.assertIn('servient_height', g.session.edited_fields)

    def test_update_update_edited_height_or_position_change_height_and_units_type(self):
        with main.app.test_request_context():
            self.build_session()
            g.session.add_lon_charge_state.structure_position_and_dimension = {'height': '10', 'units': 'metres',
                                                                               'extent-covered': 'all of the extent'}
            g.session.redirect_route = REDIRECT_ROUTE

            ReviewRouter.update_edited_height_or_position({'height': 'unlimited height',
                                                           'extent-covered': 'all of the extent'})
            self.assertTrue(len(g.session.edited_fields) == 1)
            self.assertIn('servient_height', g.session.edited_fields)

    def test_update_update_edited_height_or_position_change_extent_type_from_all(self):
        with main.app.test_request_context():
            self.build_session()
            g.session.add_lon_charge_state.structure_position_and_dimension = {'height': 'unlimited height',
                                                                               'extent-covered': 'all of the extent'}
            g.session.redirect_route = REDIRECT_ROUTE

            ReviewRouter.update_edited_height_or_position({'height': 'unlimited height',
                                                           'extent-covered': 'some of the extent',
                                                           'part-explanatory-text': 'test area coverage'})
            self.assertTrue(len(g.session.edited_fields) == 1)
            self.assertIn('servient_position', g.session.edited_fields)

    def test_update_update_edited_height_or_position_change_extent_text(self):
        with main.app.test_request_context():
            self.build_session()
            g.session.add_lon_charge_state.structure_position_and_dimension = \
                {'height': 'unlimited height',
                 'extent-covered': 'some of the extent',
                 'part-explanatory-text': 'test area coverage'}
            g.session.redirect_route = REDIRECT_ROUTE

            ReviewRouter.update_edited_height_or_position({'height': 'unlimited height',
                                                           'extent-covered': 'some of the extent',
                                                           'part-explanatory-text': 'different test area coverage'})
            self.assertTrue(len(g.session.edited_fields) == 1)
            self.assertIn('servient_position', g.session.edited_fields)

    def test_update_update_edited_height_or_position_change_extent_type_to_all(self):
        with main.app.test_request_context():
            self.build_session()
            g.session.add_lon_charge_state.structure_position_and_dimension = \
                {'height': 'unlimited height',
                 'extent-covered': 'some of the extent',
                 'part-explanatory-text': 'test area coverage'}
            g.session.redirect_route = REDIRECT_ROUTE

            ReviewRouter.update_edited_height_or_position({'height': 'unlimited height',
                                                           'extent-covered': 'all of the extent'})
            self.assertTrue(len(g.session.edited_fields) == 1)
            self.assertIn('servient_position', g.session.edited_fields)

    def test_update_update_edited_height_or_position_change_everything(self):
        with main.app.test_request_context():
            self.build_session()
            g.session.add_lon_charge_state.structure_position_and_dimension = {'height': 'unlimited height',
                                                                               'extent-covered': 'all of the extent'}
            g.session.redirect_route = REDIRECT_ROUTE

            ReviewRouter.update_edited_height_or_position({'height': '20', 'units': 'feet',
                                                           'extent-covered': 'some of the extent',
                                                           'part-explanatory-text': 'different test area coverage'})
            self.assertTrue(len(g.session.edited_fields) == 2)
            self.assertIn('servient_height', g.session.edited_fields)
            self.assertIn('servient_position', g.session.edited_fields)

    def test_update_edited_filename_field_with_redirect_route_not_set(self):
        """Should not update edited_fields if the redirect_route in session is not set."""
        with main.app.test_request_context():
            self.build_session()
            g.session.filenames = {'form_a': '', 'temporary_lon_cert': '', 'definitive_lon_cert': ''}
            g.session.redirect_route = None

            ReviewRouter.update_edited_filename_field({'form_a': '', 'temporary_lon_cert': '',
                                                       'definitive_lon_cert': ''})
            self.assertTrue(len(g.session.edited_fields) == 0)

    def test_update_edited_filename_field(self):
        """Should not update edited_fields if the redirect_route in session is not set."""
        with main.app.test_request_context():
            self.build_session()
            g.session.filenames = {'form_a': '', 'temporary_lon_cert': '', 'definitive_lon_cert': ''}
            g.session.redirect_route = REDIRECT_ROUTE

            ReviewRouter.update_edited_filename_field({'form_a': 'x', 'temporary_lon_cert': 'x',
                                                       'definitive_lon_cert': 'x'})
            self.assertTrue(len(g.session.edited_fields) == 3)
            self.assertIn('form_a_file', g.session.edited_fields)
            self.assertIn('temporary_lon_file', g.session.edited_fields)
            self.assertIn('definitive_lon_file', g.session.edited_fields)

    @staticmethod
    def build_session():
        g.session = MagicMock()
        g.session.add_lon_charge_state = LightObstructionNoticeItem()
        g.session.edited_fields = {}
        g.trace_id = 'some trace id'
