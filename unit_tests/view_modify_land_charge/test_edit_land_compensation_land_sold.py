from maintain_frontend import main
from flask_testing import TestCase as TestCase
from unit_tests.utilities import Utilities
from unittest.mock import patch
from flask import url_for
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.constants.permissions import Permissions

ADD_CHARGE_STATE = LocalLandChargeItem()
LAND_COMPENSATION_LAND_SOLD_PATH = 'maintain_frontend.view_modify_land_charge.edit_land_compensation_land_sold'
VALID_DATA = {
    'land-sold-description': 'land sold info',
    'land-works-particulars': 'works particulars info',
}


class TestEditLandCompensationLandSold(TestCase):
    render_templates = False

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    @patch('{}.LandCompensationLandSoldValidator'.format(LAND_COMPENSATION_LAND_SOLD_PATH))
    def test_land_compensation_land_sold_post_success(self, mock_validator):
        mock_validator.validate.return_value.errors = []
        self.mock_session.return_value.add_charge_state = ADD_CHARGE_STATE
        ADD_CHARGE_STATE.local_land_charge = 1
        self.mock_session.return_value.edited_fields = []

        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        response = self.client.post(url_for('modify_land_charge.post_land_compensation_land_sold'), data=VALID_DATA)
        self.assertIn('land_sold_description', self.mock_session.return_value.edited_fields)
        self.assertIn('land_works_particulars', self.mock_session.return_value.edited_fields)
        self.assertStatus(response, 302)
        self.assertRedirects(response, url_for('modify_land_charge.modify_land_charge', local_land_charge="LLC-1"))

    @patch('{}.LandCompensationLandSoldValidator'.format(LAND_COMPENSATION_LAND_SOLD_PATH))
    def test_land_compensation_land_sold_post_validation_error(self, mock_validator):
        mock_validator.validate.return_value.errors = [{'field': 'validation error'}]
        self.mock_session.return_value.add_charge_state = ADD_CHARGE_STATE
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        response = self.client.post(url_for('modify_land_charge.post_land_compensation_land_sold'), data={
            'land-sold-description': '',
            'land-works-particulars': 'e',
        })

        self.assertStatus(response, 400)
        self.assert_template_used('land_compensation_land_sold.html')

    def test_land_compensation_land_sold_post_without_session(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        self.mock_session.return_value.add_charge_state = None

        try:
            response = self.client.post(url_for('modify_land_charge.post_land_compensation_land_sold'),
                                        data=VALID_DATA)
        except Exception:
            self.assertStatus(response, 302)
            self.assert_redirects(response, '/error')

    @patch('{}.LandCompensationLandSoldValidator'.format(LAND_COMPENSATION_LAND_SOLD_PATH))
    def test_land_compensation_land_sold_post_exception(self, mock_validator):
        mock_validator.validate.side_effect = Exception('test exception')

        self.mock_session.return_value.add_charge_state = ADD_CHARGE_STATE
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        response = self.client.post(url_for('modify_land_charge.post_land_compensation_land_sold'), data={
            'land-sold-description': '',
            'land-works-particulars': 'e',
        })

        self.assertStatus(response, 302)
        self.assert_redirects(response, '/error')

    def test_land_compensation_land_sold_get_with_session(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        response = self.client.get(url_for('modify_land_charge.get_land_compensation_land_sold'))
        self.assertStatus(response, 200)
        self.assert_template_used('land_compensation_land_sold.html')

    def test_land_compensation_land_sold_get_without_session(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        self.mock_session.return_value.add_charge_state = None

        response = self.client.get(url_for('modify_land_charge.get_land_compensation_land_sold'))
        self.assertStatus(response, 302)
        self.assert_redirects(response, '/error')

    @patch('{}.render_template'.format(LAND_COMPENSATION_LAND_SOLD_PATH))
    def test_land_compensation_land_sold_render_exception(self, mock_render):
        self.mock_session.return_value.add_charge_state = ADD_CHARGE_STATE
        mock_render.side_effect = Exception('test exception')
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]
        response = self.client.get(url_for('modify_land_charge.get_land_compensation_land_sold'))
        self.assertStatus(response, 302)
        self.assertRedirects(response, "/error")
