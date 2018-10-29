from maintain_frontend import main
from flask import url_for
from flask_testing import TestCase
from unittest.mock import patch, call
from unit_tests.utilities import Utilities
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.models import Category, SubCategory


class TestSubCategory(TestCase):

    def create_app(self):
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    @patch('maintain_frontend.add_land_charge.sub_category.current_app')
    def test_get_sub_category_redirects_to_new_when_state_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_sub_category'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.sub_category.current_app')
    def test_post_sub_category_redirects_to_new_when_state_none(self, mock_current_app):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.add_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_sub_category'))

        calls = [call("Redirecting to: %s", "/add-local-land-charge")]
        mock_current_app.logger.info.assert_has_calls(calls)
        self.assert_status(response, 302)
        self.assertRedirects(response, url_for('add_land_charge.new'))

    @patch('maintain_frontend.add_land_charge.sub_category.CategoryService')
    def test_get_sub_category_success(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        sub1 = SubCategory("test1", "Test 1")
        sub2 = SubCategory("test2", "Test 2")

        category = Category(name="top-level",
                            display_name="Top Level",
                            sub_categories=[sub1, sub2],
                            parent=None,
                            statutory_provisions=[],
                            instruments=[])

        mock_service.get_category_parent_info.return_value = category

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_sub_category'))

        self.assert_status(response, 200)
        self.assert_template_used('sub_categories.html')
        self.assertIn("top level", response.data.decode())
        self.assertIn("Test 1", response.data.decode())
        self.assertIn("Test 2", response.data.decode())

    @patch('maintain_frontend.add_land_charge.sub_category.CategoryService')
    def test_get_sub_category_success_land_compensation(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Land compensation"

        category = Category(name="Land compensation",
                            display_name="Land compensation",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=[],
                            instruments=[])

        mock_service.get_category_parent_info.return_value = category

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_sub_category'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for("add_land_charge.get_all_legal_document"))

    @patch('maintain_frontend.add_land_charge.sub_category.CategoryService')
    def test_get_sub_category_success_no_sub_no_prov_no_instrument(self, mock_service):
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

        mock_service.get_category_parent_info.return_value = category

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_sub_category'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for("add_land_charge.search_law"))

    @patch('maintain_frontend.add_land_charge.sub_category.CategoryService')
    def test_get_sub_category_success_no_sub_multiple_prov_no_instrument(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        category = Category(name="top-level",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=["abc", "def"],
                            instruments=[])

        mock_service.get_category_parent_info.return_value = category

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_sub_category'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for("add_land_charge.get_law"))

    @patch('maintain_frontend.add_land_charge.sub_category.CategoryService')
    def test_get_sub_category_success_no_sub_one_prov_no_instrument(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        category = Category(name="top-level",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=["abc"],
                            instruments=[])

        mock_service.get_category_parent_info.return_value = category

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_sub_category'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for("add_land_charge.get_all_legal_document"))

    @patch('maintain_frontend.add_land_charge.sub_category.CategoryService')
    def test_get_sub_category_success_no_sub_one_prov_multiple_instruments(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        category = Category(name="top-level",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=["abc"],
                            instruments=["abc", "def"])

        mock_service.get_category_parent_info.return_value = category

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_sub_category'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for("add_land_charge.get_legal_document"))

    @patch('maintain_frontend.add_land_charge.sub_category.CategoryService')
    def test_get_sub_category_success_no_sub_one_prov_one_instruments(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        category = Category(name="top-level",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=["abc"],
                            instruments=["abc"])

        mock_service.get_category_parent_info.return_value = category

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_sub_category'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for("add_land_charge.get_law_document_confirmation"))

    @patch('maintain_frontend.add_land_charge.sub_category.CategoryService')
    def test_get_sub_category_success_no_sub_one_prov_one_instruments_lons(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        category = Category(name="Light obstruction notice",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=["abc"],
                            instruments=["abc"])

        mock_service.get_category_parent_info.return_value = category

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.get(url_for('add_land_charge.get_sub_category'))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for("add_lon.new"))

    @patch('maintain_frontend.add_land_charge.sub_category.CategoryService')
    def test_post_sub_category_validation_errors(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        sub1 = SubCategory("test1", "Test 1")
        sub2 = SubCategory("test2", "Test 2")

        category = Category(name="abc",
                            display_name="Top Level",
                            sub_categories=[sub1, sub2],
                            parent=None,
                            statutory_provisions=["abc"],
                            instruments=["abc"])

        mock_service.get_category_parent_info.return_value = category

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_sub_category'))

        self.assert_status(response, 400)
        self.assert_template_used('sub_categories.html')
        self.assertIn("top level", response.data.decode())
        self.assertIn("Test 1", response.data.decode())
        self.assertIn("Test 2", response.data.decode())
        self.assertIn("There are errors on this page", response.data.decode())
        self.assertIn("Choose one option", response.data.decode())

    @patch('maintain_frontend.add_land_charge.sub_category.CategoryService')
    def test_post_sub_category_more_sub_categories(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        sub1 = SubCategory("test1", "Test 1")
        sub2 = SubCategory("test2", "Test 2")

        category = Category(name="abc",
                            display_name="Top Level",
                            sub_categories=[sub1, sub2],
                            parent=None,
                            statutory_provisions=["abc"],
                            instruments=["abc"])

        mock_service.get_sub_category_info.return_value = category

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_sub_category'),
                                    data={'charge-sub-category': 'ABC'})

        self.assert_status(response, 200)
        self.assert_template_used('sub_categories.html')
        self.assertIn("top level", response.data.decode())
        self.assertIn("Test 1", response.data.decode())
        self.assertIn("Test 2", response.data.decode())

    @patch('maintain_frontend.add_land_charge.sub_category.CategoryService')
    def test_post_sub_category_success_land_compensation(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        category = Category(name="Land compensation",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=["abc"],
                            instruments=["abc"])

        mock_service.get_sub_category_info.return_value = category

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_sub_category'),
                                    data={'charge-sub-category': 'Land compensation'})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for("add_land_charge.get_all_legal_document"))

    @patch('maintain_frontend.add_land_charge.sub_category.CategoryService')
    def test_post_sub_category_success_no_sub_no_prov_no_instrument(self, mock_service):
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

        mock_service.get_sub_category_info.return_value = category

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_sub_category'),
                                    data={'charge-sub-category': 'abc'})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for("add_land_charge.search_law"))

    @patch('maintain_frontend.add_land_charge.sub_category.CategoryService')
    def test_post_sub_category_success_no_sub_multiple_prov_no_instrument(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        category = Category(name="top-level",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=["abc", "def"],
                            instruments=[])

        mock_service.get_sub_category_info.return_value = category

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_sub_category'),
                                    data={'charge-sub-category': 'abc'})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for("add_land_charge.get_law"))

    @patch('maintain_frontend.add_land_charge.sub_category.CategoryService')
    def test_post_sub_category_success_no_sub_one_prov_no_instrument(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        category = Category(name="top-level",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=["abc"],
                            instruments=[])

        mock_service.get_sub_category_info.return_value = category

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_sub_category'),
                                    data={'charge-sub-category': 'abc'})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for("add_land_charge.get_all_legal_document"))

    @patch('maintain_frontend.add_land_charge.sub_category.CategoryService')
    def test_post_sub_category_success_no_sub_one_prov_multiple_instruments(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        category = Category(name="top-level",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=["abc"],
                            instruments=["abc", "def"])

        mock_service.get_sub_category_info.return_value = category

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_sub_category'),
                                    data={'charge-sub-category': 'abc'})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for("add_land_charge.get_legal_document"))

    @patch('maintain_frontend.add_land_charge.sub_category.CategoryService')
    def test_post_sub_category_success_no_sub_one_prov_one_instruments(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        category = Category(name="top-level",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=["abc"],
                            instruments=["abc"])

        mock_service.get_sub_category_info.return_value = category

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_sub_category'),
                                    data={'charge-sub-category': 'abc'})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for("add_land_charge.get_law_document_confirmation"))

    @patch('maintain_frontend.add_land_charge.sub_category.CategoryService')
    def test_post_sub_category_success_no_sub_one_prov_one_instruments_lons(self, mock_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        category = Category(name="Light obstruction notice",
                            display_name="Top Level",
                            sub_categories=[],
                            parent=None,
                            statutory_provisions=["abc"],
                            instruments=["abc"])

        mock_service.get_sub_category_info.return_value = category

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_sub_category'),
                                    data={'charge-sub-category': 'Light obstruction notice'})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for("add_lon.new"))

    def test_post_sub_category_success_dont_know_category(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        state = LocalLandChargeItem()
        state.geometry = "abc"
        state.charge_type = "Top Level"

        self.mock_session.return_value.add_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_llc]

        response = self.client.post(url_for('add_land_charge.post_sub_category'),
                                    data={'charge-sub-category': "I don't know the charge category"})

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for("add_land_charge.get_subcategory_not_known"))
