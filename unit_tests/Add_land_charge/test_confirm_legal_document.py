from maintain_frontend import main
from flask import url_for
from flask_testing import TestCase
from unittest.mock import patch, call
from unit_tests.utilities import Utilities
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.models import Category


class TestConfirmLegalDocument(TestCase):

    def create_app(self):
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    @patch('maintain_frontend.add_land_charge.confirm_legal_document.current_app')
    def test_get_legal_document_redirects_to_new_when_state_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_legal_document'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.confirm_legal_document.current_app')
    def test_get_legal_document_redirects_to_new_when_charge_type_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = None

        response = self.client.get(url_for('add_land_charge.get_legal_document'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.confirm_legal_document.current_app')
    def test_get_legal_document_redirects_to_new_when_details_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = None

        response = self.client.get(url_for('add_land_charge.get_legal_document'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.confirm_legal_document.current_app')
    def test_get_legal_document_redirects_to_new_when_stat_prov_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        category = Category(name="top-level",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=[],
                            instruments=None)

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = category

        response = self.client.get(url_for('add_land_charge.get_legal_document'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.confirm_legal_document.current_app')
    def test_get_legal_document_redirects_to_new_when_stat_prov_empty(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        category = Category(name="top-level",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=[],
                            instruments=[])

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = category

        response = self.client.get(url_for('add_land_charge.get_legal_document'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    def test_get_legal_document_successful(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"
        state.statutory_provision = "test statutory provision"

        category = Category(name="top-level",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=[],
                            instruments=["abc", "def", "ghi"])

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = category

        response = self.client.get(url_for('add_land_charge.get_legal_document'))

        self.assert_status(response, 200)
        self.assert_template_used('confirm_legal_document.html')
        self.assertIn("test statutory provision", response.data.decode())
        self.assertIn("abc", response.data.decode())
        self.assertIn("def", response.data.decode())
        self.assertIn("ghi", response.data.decode())

    @patch('maintain_frontend.add_land_charge.confirm_legal_document.current_app')
    def test_post_legal_document_redirects_to_new_when_state_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.get_legal_document'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.confirm_legal_document.current_app')
    def test_post_legal_document_redirects_to_new_when_charge_type_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = None

        response = self.client.post(url_for('add_land_charge.get_legal_document'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.confirm_legal_document.current_app')
    def test_post_legal_document_redirects_to_new_when_details_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = None

        response = self.client.post(url_for('add_land_charge.get_legal_document'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.confirm_legal_document.current_app')
    def test_post_legal_document_redirects_to_new_when_stat_prov_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        category = Category(name="top-level",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=[],
                            instruments=None)

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = category

        response = self.client.post(url_for('add_land_charge.get_legal_document'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.confirm_legal_document.current_app')
    def test_post_legal_document_redirects_to_new_when_stat_prov_empty(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        category = Category(name="top-level",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=[],
                            instruments=[])

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = category

        response = self.client.post(url_for('add_land_charge.get_legal_document'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    def test_post_legal_document_validation_errors(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"
        state.statutory_provision = "test statutory provision"

        category = Category(name="top-level",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=[],
                            instruments=["abc", "def", "ghi"])

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = category

        response = self.client.post(url_for('add_land_charge.get_legal_document'), data={"confirm-instrument": None})

        self.assert_status(response, 400)
        self.assert_template_used('confirm_legal_document.html')
        self.assertIn("test statutory provision", response.data.decode())
        self.assertIn("abc", response.data.decode())
        self.assertIn("def", response.data.decode())
        self.assertIn("ghi", response.data.decode())
        self.assertIn("There are errors on this page", response.data.decode())
        self.assertIn("Choose one option", response.data.decode())

    def test_post_legal_document_successful_confirmation(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"
        state.statutory_provision = "test statutory provision"

        category = Category(name="top-level",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=[],
                            instruments=["abc", "def", "ghi"])

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = category
        self.mock_session.return_value.category_confirmation = True

        response = self.client.post(url_for('add_land_charge.get_legal_document'), data={"confirm-instrument": "abc"})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_law_document_confirmation'))

    def test_post_legal_document_successful_financial(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Financial"
        state.statutory_provision = "test statutory provision"

        category = Category(name="top-level",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=[],
                            instruments=["abc", "def", "ghi"])

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = category
        self.mock_session.return_value.category_confirmation = False

        response = self.client.post(url_for('add_land_charge.get_legal_document'), data={"confirm-instrument": "abc"})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_financial_charge'))

    def test_post_legal_document_successful_land_compensation(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Land compensation"
        state.statutory_provision = "test statutory provision"

        category = Category(name="top-level",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=[],
                            instruments=["abc", "def", "ghi"])

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = category
        self.mock_session.return_value.category_confirmation = False

        response = self.client.post(url_for('add_land_charge.get_legal_document'), data={"confirm-instrument": "abc"})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_land_compensation_type'))

    def test_post_legal_document_successful_lon(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Light obstruction notice"
        state.statutory_provision = "test statutory provision"

        category = Category(name="top-level",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=[],
                            instruments=["abc", "def", "ghi"])

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = category
        self.mock_session.return_value.category_confirmation = False

        response = self.client.post(url_for('add_land_charge.get_legal_document'), data={"confirm-instrument": "abc"})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_lon.new'))

    def test_post_legal_document_successful_charge_date(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Charge category"
        state.statutory_provision = "test statutory provision"

        category = Category(name="top-level",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=[],
                            instruments=["abc", "def", "ghi"])

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = category
        self.mock_session.return_value.category_confirmation = False

        response = self.client.post(url_for('add_land_charge.get_legal_document'), data={"confirm-instrument": "abc"})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_charge_date'))

    @patch('maintain_frontend.add_land_charge.confirm_legal_document.current_app')
    def test_get_all_legal_documents_redirects_to_new_when_state_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_all_legal_document'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.confirm_legal_document.current_app')
    def test_get_all_legal_documents_redirects_to_new_when_charge_type_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = None

        response = self.client.get(url_for('add_land_charge.get_all_legal_document'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.confirm_legal_document.CategoryService')
    def test_get_all_legal_documents_successful(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"
        state.statutory_provision = "test statutory provision"

        mock_service.get_all_instruments.return_value = ["abc", "def"]

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_all_legal_document'))

        self.assert_status(response, 200)
        self.assert_template_used('instruments.html')
        self.assertIn("abc", response.data.decode())
        self.assertIn("def", response.data.decode())

    @patch('maintain_frontend.add_land_charge.confirm_legal_document.current_app')
    def test_post_all_legal_documents_redirects_to_new_when_state_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_all_legal_document'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.confirm_legal_document.current_app')
    def test_post_all_legal_documents_redirects_to_new_when_charge_type_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = None

        response = self.client.post(url_for('add_land_charge.post_all_legal_document'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.confirm_legal_document.CategoryService')
    def test_post_all_legal_documents_successful_when_not_supplied(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"
        state.statutory_provision = "test statutory provision"
        state.instrument = None

        mock_service.return_value.get_all_instruments.return_value = ["abc", "def"]

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_confirmation = False

        response = self.client.post(url_for('add_land_charge.post_all_legal_document'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_charge_date'))
        self.assertIsNone(self.mock_session.return_value.add_charge_state.instrument)

    @patch('maintain_frontend.add_land_charge.confirm_legal_document.CategoryService')
    def test_post_all_legal_documents_successful_when_supplied(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"
        state.statutory_provision = "test statutory provision"
        state.instrument = None

        mock_service.return_value.get_all_instruments.return_value = ["abc", "def"]

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_confirmation = False

        response = self.client.post(url_for('add_land_charge.post_all_legal_document'),
                                    data={"confirm-instrument": "abc"})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_charge_date'))
        self.assertEqual("abc", self.mock_session.return_value.add_charge_state.instrument)
