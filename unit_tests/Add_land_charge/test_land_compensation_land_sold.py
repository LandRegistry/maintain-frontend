from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.constants.permissions import Permissions
from flask import url_for
from unittest.mock import patch, PropertyMock, call

LAND_SOLD_PATH = 'maintain_frontend.add_land_charge.land_compensation_land_sold'


class TestLandCompensationLandSold(TestCase):

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_get_land_compensation_land_sold_success(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_land_compensation_land_sold'))

        self.assert_status(response, 200)
        self.assert_template_used('land_compensation_land_sold.html')

    def test_get_land_compensation_land_sold_add_charge_state_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_land_compensation_land_sold'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('{}.g'.format(LAND_SOLD_PATH))
    def test_get_land_compensation_land_sold_exception(self, mock_g):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        raise_exception = PropertyMock(side_effect=Exception('test exception'))
        type(mock_g).session = raise_exception

        try:
            response = self.client.get(url_for('add_land_charge.get_land_compensation_land_sold'))
        except Exception:
            self.assertStatus(response, 302)
            self.assertRedirects(response, url_for("add_land_charge.new"))

    def test_get_land_compensation_land_sold_no_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = []

        response = self.client.get(url_for('add_land_charge.get_land_compensation_land_sold'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')

    @patch('{}.ReviewRouter'.format(LAND_SOLD_PATH))
    def test_post_land_compensation_land_sold_success(self, mock_review_router):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        mock_review_router.get_redirect_url.return_value = url_for('add_land_charge.get_charge_date')

        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_land_compensation_land_sold'),
                                    data={'land-sold-description': 'description',
                                          'land-works-particulars': 'particulars'})

        calls = [call('land_sold_description', 'description'),
                 call('land_works_particulars', 'particulars')]
        mock_review_router.update_edited_field.assert_has_calls(calls)

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_charge_date'))

    def test_post_land_compensation_land_sold_add_charge_state_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_land_compensation_land_sold'),
                                    data={'land-sold-description': 'description',
                                          'land-works-particulars': 'particulars'})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    def test_post_land_compensation_land_sold_max_length_validation(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_land_compensation_land_sold'),
                                    data={'land-sold-description': 'a' * 401,
                                    'land-works-particulars': 'a' * 401})

        self.assert_status(response, 400)
        self.assert_template_used('land_compensation_land_sold.html')
        self.assertIn('Answer too long', response.data.decode())
        self.assertIn('Answer must be shorter than 400 characters (about 60 words)', response.data.decode())

    def test_post_land_compensation_land_sold_no_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = []

        response = self.client.get(url_for('add_land_charge.post_land_compensation_land_sold'),
                                   data={'land-sold-description': 'description',
                                         'land-works-particulars': 'particulars'})

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')
