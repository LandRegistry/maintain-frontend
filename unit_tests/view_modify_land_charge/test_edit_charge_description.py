from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from unittest.mock import patch
from flask import url_for
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.constants.permissions import Permissions


class TestEditLandChargeDescription(TestCase):

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_redirects_to_edit_location_when_state_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        self.mock_session.return_value.add_charge_state = None

        response = self.client.get(url_for('modify_land_charge.get_charge_description'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/error')

    def test_renders_when_previous_information_set(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state

        response = self.client.get(url_for('modify_land_charge.get_charge_description'))

        self.assertStatus(response, 200)
        self.assert_template_used('charge_description.html')

    def test_renders_with_data_when_previously_set(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        state = LocalLandChargeItem()
        state.supplementary_information = "test-supplementary-information"

        self.mock_session.return_value.add_charge_state = state

        response = self.client.get(url_for('modify_land_charge.get_charge_description'))

        self.assertStatus(response, 200)
        self.assert_template_used('charge_description.html')
        self.assertIn('test-supplementary-information', response.data.decode())

    def test_post_redirects_to_edit_location_when_state_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        self.mock_session.return_value.add_charge_state = None

        response = self.client.post(url_for('modify_land_charge.post_charge_description'),
                                    data={
                                        'charge-description': 'test-charge-description'
        })

        self.assert_status(response, 302)
        self.assertRedirects(response, '/error')

    def test_post_renders_when_previous_information_set(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        state = LocalLandChargeItem()
        state.local_land_charge = 12345678

        self.mock_session.return_value.add_charge_state = state

        response = self.client.post(url_for('modify_land_charge.post_charge_description'),
                                    data={
                                        'charge-description': 'test-charge-description'
        })

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('modify_land_charge.modify_land_charge', local_land_charge='LLC-FCDPP'))

    @patch('maintain_frontend.view_modify_land_charge.edit_charge_description.ChargeDescriptionValidator')
    def test_post_check_validation_errors(self, mock_validator):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.vary_llc]

        state = LocalLandChargeItem()
        self.mock_session.return_value.add_charge_state = state

        mock_validator.validate.return_value.errors = {'charge-description': ['some error message']}

        response = self.client.post(url_for('modify_land_charge.post_charge_description'),
                                    data={
                                        'charge-description': ''
        })

        mock_validator.validate.assert_called_with('')

        self.assert_status(response, 400)
        self.assert_context('validation_errors', {'charge-description': ['some error message']})
