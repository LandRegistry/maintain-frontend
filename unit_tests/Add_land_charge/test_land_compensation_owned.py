from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.constants.permissions import Permissions
from flask import url_for
from unittest.mock import patch, PropertyMock, call, MagicMock

LAND_COMPENSATION_OWNED_PATH = 'maintain_frontend.add_land_charge.land_compensation_owned'


class TestLandCompensationOwned(TestCase):

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_get_land_compensation_owned_success(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_land_compensation_owned'))

        self.assert_status(response, 200)
        self.assert_template_used('land_compensation_owned.html')

    def test_get_land_compensation_owned_success_with_other(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        state.land_capacity_description = 'some text'

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_land_compensation_owned'))

        self.assert_status(response, 200)
        self.assert_template_used('land_compensation_owned.html')
        self.assertEqual(self.get_context_variable('request_body')['land-owned-indicator'], 'Other')
        self.assertEqual(self.get_context_variable('request_body')['land-owned-other'], 'some text')

    def test_get_land_compensation_owned_success_freehold(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LocalLandChargeItem()
        state.land_capacity_description = 'Freehold'

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_land_compensation_owned'))

        self.assert_status(response, 200)
        self.assert_template_used('land_compensation_owned.html')
        self.assertEqual(self.get_context_variable('request_body')['land-owned-indicator'], 'Freehold')

    def test_get_land_compensation_owned_add_charge_state_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_land_compensation_owned'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('{}.g'.format(LAND_COMPENSATION_OWNED_PATH))
    def test_get_land_compensation_owned_exception(self, mock_g):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        raise_exception = PropertyMock(side_effect=Exception('test exception'))
        type(mock_g).session = raise_exception

        try:
            response = self.client.get(url_for('add_land_charge.get_land_compensation_owned'))
        except Exception:
            self.assertStatus(response, 302)
            self.assertRedirects(response, url_for("add_land_charge.new"))

    def test_get_land_compensation_owned_no_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = []

        response = self.client.get(url_for('add_land_charge.get_land_compensation_owned'))

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')

    @patch('{}.ReviewRouter'.format(LAND_COMPENSATION_OWNED_PATH))
    @patch('{}.LandCompensationOwnedValidator'.format(LAND_COMPENSATION_OWNED_PATH))
    def test_post_land_compensation_owned_success_freehold(self, mock_land_compensation_payment_validator,
                                                           mock_review_router):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        mock_review_router.get_redirect_url.return_value = url_for('add_land_charge.get_charge_date')

        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        mock_validation_errors = MagicMock()
        mock_validation_errors.errors = {}
        mock_land_compensation_payment_validator.validate.return_value = mock_validation_errors

        response = self.client.post(url_for('add_land_charge.post_land_compensation_owned'),
                                    data={'land-owned-indicator': 'Freehold', 'land-owned-other': ''})

        calls = [call('land_capacity_description', 'Freehold')]
        mock_review_router.update_edited_field.assert_has_calls(calls)

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_charge_date'))

    @patch('{}.ReviewRouter'.format(LAND_COMPENSATION_OWNED_PATH))
    @patch('{}.LandCompensationOwnedValidator'.format(LAND_COMPENSATION_OWNED_PATH))
    def test_post_land_compensation_owned_success_leasehold(self, mock_land_compensation_payment_validator,
                                                            mock_review_router):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        mock_review_router.get_redirect_url.return_value = url_for('add_land_charge.get_charge_date')

        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        mock_validation_errors = MagicMock()
        mock_validation_errors.errors = {}
        mock_land_compensation_payment_validator.validate.return_value = mock_validation_errors

        response = self.client.post(url_for('add_land_charge.post_land_compensation_owned'),
                                    data={'land-owned-indicator': 'Leasehold', 'land-owned-other': ''})

        calls = [call('land_capacity_description', 'Leasehold')]
        mock_review_router.update_edited_field.assert_has_calls(calls)

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_charge_date'))

    @patch('{}.ReviewRouter'.format(LAND_COMPENSATION_OWNED_PATH))
    @patch('{}.LandCompensationOwnedValidator'.format(LAND_COMPENSATION_OWNED_PATH))
    def test_post_land_compensation_owned_success_other(self, mock_land_compensation_payment_validator,
                                                        mock_review_router):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        mock_review_router.get_redirect_url.return_value = url_for('add_land_charge.get_charge_date')

        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        mock_validation_errors = MagicMock()
        mock_validation_errors.errors = {}
        mock_land_compensation_payment_validator.validate.return_value = mock_validation_errors

        response = self.client.post(url_for('add_land_charge.post_land_compensation_owned'),
                                    data={'land-owned-indicator': 'Other', 'land-owned-other': 'some text'})

        calls = [call('land_capacity_description', 'some text')]
        mock_review_router.update_edited_field.assert_has_calls(calls)

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_charge_date'))

    def test_post_land_compensation_owned_add_charge_state_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_land_compensation_owned'),
                                    data={'land-owned-indicator': 'Leasehold', 'land-owned-other': ''})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('{}.current_app'.format(LAND_COMPENSATION_OWNED_PATH))
    @patch('{}.LandCompensationOwnedValidator'.format(LAND_COMPENSATION_OWNED_PATH))
    def test_post_land_compensation_owned_fail_validation(self, mock_land_compensation_payment_validator,
                                                          mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        state = LocalLandChargeItem()

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        mock_validation_errors = MagicMock()
        mock_validation_errors.errors = {'field_name': 'error'}
        mock_validation_errors.summary_heading_text = 'test'
        mock_land_compensation_payment_validator.validate.return_value = mock_validation_errors

        response = self.client.post(url_for('add_land_charge.post_land_compensation_owned'),
                                    data={'land-owned-indicator': '', 'land-owned-other': ''})

        mock_current_app.logger.warning.assert_called_with('Validation errors occurred')
        self.assert_status(response, 400)
        self.assert_template_used('land_compensation_owned.html')

    def test_post_land_compensation_owned_no_permission(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = []

        response = self.client.get(url_for('add_land_charge.post_land_compensation_owned'),
                                   data={'amount-secured': '100', 'interest-paid-indicator': 'No'})

        self.assert_status(response, 302)
        self.assertRedirects(response, '/not-authorised')
