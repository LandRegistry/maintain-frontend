from maintain_frontend import main
from flask import url_for
from flask_testing import TestCase
from unittest.mock import patch, call
from unit_tests.utilities import Utilities
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.models import Category


class TestConfirmLaw(TestCase):

    def create_app(self):
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    @patch('maintain_frontend.add_land_charge.confirm_law.current_app')
    def test_get_law_redirects_to_new_when_state_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_law'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.confirm_law.current_app')
    def test_get_law_redirects_to_new_when_charge_type_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = None

        response = self.client.get(url_for('add_land_charge.get_law'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.confirm_law.current_app')
    def test_get_law_redirects_to_new_when_details_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = None

        response = self.client.get(url_for('add_land_charge.get_law'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.confirm_law.current_app')
    def test_get_law_redirects_to_new_when_stat_prov_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        category = Category(name="top-level",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=None,
                            instruments=[])

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = category

        response = self.client.get(url_for('add_land_charge.get_law'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.confirm_law.current_app')
    def test_get_law_redirects_to_new_when_stat_prov_empty(self, mock_current_app):
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

        response = self.client.get(url_for('add_land_charge.get_law'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    def test_get_law_successful(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        category = Category(name="top-level",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=["abc", "def", "ghi"],
                            instruments=[])

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = category

        response = self.client.get(url_for('add_land_charge.get_law'))

        self.assert_status(response, 200)
        self.assert_template_used('confirm_law.html')
        self.assertIn("Top Level", response.data.decode())
        self.assertIn("abc", response.data.decode())
        self.assertIn("def", response.data.decode())
        self.assertIn("ghi", response.data.decode())

    @patch('maintain_frontend.add_land_charge.confirm_law.current_app')
    def test_post_law_redirects_to_new_when_state_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.get_law'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.confirm_law.current_app')
    def test_post_law_redirects_to_new_when_charge_type_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = None

        response = self.client.post(url_for('add_land_charge.get_law'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.confirm_law.current_app')
    def test_post_law_redirects_to_new_when_details_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = None

        response = self.client.post(url_for('add_land_charge.get_law'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.confirm_law.current_app')
    def test_post_law_redirects_to_new_when_stat_prov_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        category = Category(name="top-level",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=None,
                            instruments=[])

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = category

        response = self.client.post(url_for('add_land_charge.get_law'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.confirm_law.current_app')
    def test_post_law_redirects_to_new_when_stat_prov_empty(self, mock_current_app):
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

        response = self.client.post(url_for('add_land_charge.get_law'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    def test_post_law_validation_errors(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        category = Category(name="top-level",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=["abc", "def", "ghi"],
                            instruments=[])

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = category

        response = self.client.post(url_for('add_land_charge.get_law'), data={"confirm-law-option": None})

        self.assert_status(response, 400)
        self.assert_template_used('confirm_law.html')
        self.assertIn("There are errors on this page", response.data.decode())
        self.assertIn("Choose one option", response.data.decode())

    def test_post_law_successful_no_instruments(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        category = Category(name="top-level",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=["abc", "def", "ghi"],
                            instruments=[])

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = category

        response = self.client.post(url_for('add_land_charge.get_law'), data={"confirm-law-option": "abc"})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_all_legal_document'))

    def test_post_law_successful_multiple_instruments(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        category = Category(name="top-level",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=["abc", "def", "ghi"],
                            instruments=["abc", "def"])

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = category

        response = self.client.post(url_for('add_land_charge.get_law'), data={"confirm-law-option": "abc"})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_legal_document'))

    def test_post_law_successful_financial(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Financial"

        category = Category(name="Financial",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=["abc", "def", "ghi"],
                            instruments=["abc"])

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = category

        response = self.client.post(url_for('add_land_charge.get_law'), data={"confirm-law-option": "abc"})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_financial_charge'))

    def test_post_law_successful_land_compensation(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Land compensation"

        category = Category(name="Land compensation",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=["abc", "def", "ghi"],
                            instruments=["abc"])

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = category

        response = self.client.post(url_for('add_land_charge.get_law'), data={"confirm-law-option": "abc"})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_land_compensation_type'))

    def test_post_law_successful_lon(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Light obstruction notice"

        category = Category(name="Light obstruction notice",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=["abc", "def", "ghi"],
                            instruments=["abc"])

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = category

        response = self.client.post(url_for('add_land_charge.get_law'), data={"confirm-law-option": "abc"})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_lon.new'))

    @patch('maintain_frontend.add_land_charge.confirm_law.current_app')
    def test_get_all_laws_redirects_to_new_when_state_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.search_law'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.confirm_law.current_app')
    def test_get_all_laws_redirects_to_new_when_charge_type_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = None

        response = self.client.get(url_for('add_land_charge.search_law'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.confirm_law.CategoryService')
    def test_get_all_laws_successful(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        mock_service.get_all_stat_provs.return_value = ["abc", "def"]
        response = self.client.get(url_for('add_land_charge.search_law'))

        self.assert_status(response, 200)
        self.assert_template_used('search_law.html')
        self.assertIn("abc", response.data.decode())
        self.assertIn("def", response.data.decode())

    @patch('maintain_frontend.add_land_charge.confirm_law.current_app')
    def test_post_all_laws_redirects_to_new_when_state_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_search_law'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.confirm_law.current_app')
    def test_post_all_laws_redirects_to_new_when_charge_type_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_search_law'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.confirm_law.CategoryService')
    def test_post_all_laws_validation_errors(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        mock_service.get_all_stat_provs.return_value = ["abc", "def"]

        response = self.client.post(url_for('add_land_charge.post_search_law'))

        self.assert_status(response, 400)
        self.assert_template_used('search_law.html')
        self.assertIn("abc", response.data.decode())
        self.assertIn("def", response.data.decode())
        self.assertIn("There are errors on this page", response.data.decode())
        self.assertIn("Law is required", response.data.decode())

    @patch('maintain_frontend.add_land_charge.confirm_law.CategoryService')
    def test_post_all_laws_validation_errors_not_on_list(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        mock_service.get_all_stat_provs.return_value = ["abc", "def"]

        response = self.client.post(url_for('add_land_charge.post_search_law'), data={"legislation": "ghi"})

        self.assert_status(response, 400)
        self.assert_template_used('search_law.html')
        self.assertIn("abc", response.data.decode())
        self.assertIn("def", response.data.decode())
        self.assertIn("There are errors on this page", response.data.decode())
        self.assertIn("ghi is not a valid selection for law", response.data.decode())

    @patch('maintain_frontend.add_land_charge.confirm_law.CategoryService')
    def test_post_all_laws_success_no_instruments(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        category = Category(name="Light obstruction notice",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=[],
                            instruments=[])

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = category

        mock_service.get_all_stat_provs.return_value = ["abc", "def"]

        response = self.client.post(url_for('add_land_charge.post_search_law'), data={"legislation": "abc"})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_all_legal_document'))

    @patch('maintain_frontend.add_land_charge.confirm_law.CategoryService')
    def test_post_all_laws_success_multiple_instruments(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        category = Category(name="Light obstruction notice",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=[],
                            instruments=["abc", "def"])

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = category

        mock_service.get_all_stat_provs.return_value = ["abc", "def"]

        response = self.client.post(url_for('add_land_charge.post_search_law'), data={"legislation": "abc"})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_legal_document'))

    @patch('maintain_frontend.add_land_charge.confirm_law.CategoryService')
    def test_post_all_laws_success_financial(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Financial"

        category = Category(name="Financial",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=[],
                            instruments=["abc"])

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = category

        mock_service.get_all_stat_provs.return_value = ["abc", "def"]

        response = self.client.post(url_for('add_land_charge.post_search_law'), data={"legislation": "abc"})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_financial_charge'))

    @patch('maintain_frontend.add_land_charge.confirm_law.CategoryService')
    def test_post_all_laws_success_land_compensation(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Land compensation"

        category = Category(name="Land compensation",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=[],
                            instruments=["abc"])

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = category

        mock_service.get_all_stat_provs.return_value = ["abc", "def"]

        response = self.client.post(url_for('add_land_charge.post_search_law'), data={"legislation": "abc"})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_land_compensation_type'))

    @patch('maintain_frontend.add_land_charge.confirm_law.CategoryService')
    def test_post_all_laws_success_lon(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Light obstruction notice"

        category = Category(name="Light obstruction notice",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=[],
                            instruments=["abc"])

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = category

        mock_service.get_all_stat_provs.return_value = ["abc", "def"]

        response = self.client.post(url_for('add_land_charge.post_search_law'), data={"legislation": "abc"})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_lon.new'))

    @patch('maintain_frontend.add_land_charge.confirm_law.CategoryService')
    def test_post_all_laws_success_charge_date(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top level"

        category = Category(name="Top Level",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=[],
                            instruments=["abc"])

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = category

        mock_service.get_all_stat_provs.return_value = ["abc", "def"]

        response = self.client.post(url_for('add_land_charge.post_search_law'), data={"legislation": "abc"})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_charge_date'))

    @patch('maintain_frontend.add_land_charge.confirm_law.CategoryService')
    def test_post_all_laws_success_nojs_charge_date(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top level"

        category = Category(name="Top Level",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=[],
                            instruments=["abc"])

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]
        self.mock_session.return_value.category_details = category

        mock_service.get_all_stat_provs.return_value = ["abc", "def"]

        response = self.client.post(url_for('add_land_charge.post_search_law'), data={"legislation-nojs": "abc"})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.get_charge_date'))
