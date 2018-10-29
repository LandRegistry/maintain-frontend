from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from flask import url_for
from unittest.mock import patch
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LightObstructionNoticeItem


class TestPaymentMethod(TestCase):
    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_payment_method_redirects_to_new_when_state_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.add_lon_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        response = self.client.get(url_for('add_lon.get_payment_method'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_lon.new'))

    def test_payment_method_get(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LightObstructionNoticeItem()
        self.mock_session.return_value.add_lon_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        payment_info = {
            'payment_method': 'govuk',
            'payment_ref': 'test_reference',
            'no_payment_notes': ''
        }
        self.mock_session.payment_info = payment_info

        response = self.client.get(url_for('add_lon.get_payment_method'))

        self.assert_status(response, 200)
        self.assert_template_used('payment_method.html')

    def test_payment_method_no_permission_redirects(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        self.mock_session.return_value.user.permissions = []

        response = self.client.get(url_for('add_lon.get_payment_method'))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')

        response = self.client.get(url_for('add_lon.post_payment_method'))
        self.assertStatus(response, 302)
        self.assertRedirects(response, '/not-authorised')

    @patch('maintain_frontend.add_lon.payment_method.request')
    @patch('maintain_frontend.add_lon.payment_method.PaymentMethodValidator')
    def test_post_valid_payment_method(self, mock_validator, mock_request):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        mock_request.form = {
            'payment_method': 'govuk',
            'payment_ref': 'test_reference',
            'no_payment_notes': ''
        }

        mock_validator.validate.return_value.errors = None

        response = self.client.post(url_for('add_lon.post_payment_method'))

        self.assert_status(response, 302)
        self.assertEqual(self.mock_session.return_value.payment_info.payment_method, 'govuk')
        self.assertRedirects(response, url_for('add_lon.get_applicant_info'))

    @patch('maintain_frontend.add_lon.payment_method.request')
    @patch('maintain_frontend.add_lon.payment_method.PaymentMethodValidator')
    def test_post_invalid_payment_method(self, mock_validator, mock_request):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        mock_request.form = {
            'payment_method': 'govuk',
            'payment_ref': 'test_reference',
            'no_payment_notes': ''
        }

        error = {'payment_method': ['some error message']}
        mock_validator.validate.return_value.errors = error

        response = self.client.post(url_for('add_lon.post_payment_method'))

        self.assert_context('validation_errors', error)
        self.assert_status(response, 400)
        self.assert_template_used('payment_method.html')
