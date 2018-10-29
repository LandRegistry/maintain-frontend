from unittest import TestCase
from unittest.mock import patch, MagicMock

from flask import g

from maintain_frontend import main
from maintain_frontend.dependencies.maintain_api.categories import CategoryService
from maintain_frontend.exceptions import ApplicationError
from unit_tests.utilities import Utilities


class TestCategories(TestCase):
    def setUp(self):
        self.app = main.app.test_client()
        Utilities.mock_session_cookie_unittest(self)

    @patch('maintain_frontend.dependencies.maintain_api.categories.MAINTAIN_API_URL', 'abc')
    @patch('maintain_frontend.dependencies.maintain_api.categories.current_app')
    def test_get_top_level(self, mock_current_app):
        with main.app.test_request_context():
            g.requests = MagicMock()
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = [
                {
                    "permission": None,
                    "display-name": "Test 1",
                    "name": "test-1"
                },
                {
                    "permission": None,
                    "display-name": "Test 2",
                    "name": "test-2"
                }
            ]

            g.requests.get.return_value = response

            response = CategoryService.get_categories()

            self.assertEqual(2, len(response))
            self.assertEqual("test-1", response[0]['name'])
            self.assertEqual("Test 1", response[0]['display'])
            self.assertEqual("test-2", response[1]['name'])
            self.assertEqual("Test 2", response[1]['display'])

            g.requests.get.assert_called_with("{}/categories".format('abc'))
            mock_current_app.logger.info.assert_called()

    @patch('maintain_frontend.dependencies.maintain_api.categories.MAINTAIN_API_URL', 'abc')
    @patch('maintain_frontend.dependencies.maintain_api.categories.current_app')
    def test_get_top_level_filtered_permissions(self, mock_current_app):
        with main.app.test_request_context():
            g.requests = MagicMock()
            g.session = MagicMock()
            g.session.user.permissions = []
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = [
                {
                    "permission": "TEST-PERMISSION",
                    "display-name": "Test 1",
                    "name": "test-1"
                },
                {
                    "permission": None,
                    "display-name": "Test 2",
                    "name": "test-2"
                }
            ]

            g.requests.get.return_value = response

            response = CategoryService.get_categories()

            self.assertEqual(1, len(response))
            self.assertEqual("test-2", response[0]['name'])
            self.assertEqual("Test 2", response[0]['display'])

            g.requests.get.assert_called_with("{}/categories".format('abc'))
            mock_current_app.logger.info.assert_called()

    @patch('maintain_frontend.dependencies.maintain_api.categories.MAINTAIN_API_URL', 'abc')
    @patch('maintain_frontend.dependencies.maintain_api.categories.current_app')
    def test_get_top_level_permissions(self, mock_current_app):
        with main.app.test_request_context():
            g.requests = MagicMock()
            g.session = MagicMock()
            g.session.user.permissions = ["TEST-PERMISSION"]
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = [
                {
                    "permission": "TEST-PERMISSION",
                    "display-name": "Test 1",
                    "name": "test-1"
                },
                {
                    "permission": None,
                    "display-name": "Test 2",
                    "name": "test-2"
                }
            ]

            g.requests.get.return_value = response

            response = CategoryService.get_categories()

            self.assertEqual(2, len(response))
            self.assertEqual("test-1", response[0]['name'])
            self.assertEqual("Test 1", response[0]['display'])
            self.assertEqual("test-2", response[1]['name'])
            self.assertEqual("Test 2", response[1]['display'])

            g.requests.get.assert_called_with("{}/categories".format('abc'))
            mock_current_app.logger.info.assert_called()

    @patch('maintain_frontend.dependencies.maintain_api.categories.MAINTAIN_API_URL', 'abc')
    @patch('maintain_frontend.dependencies.maintain_api.categories.current_app')
    def test_get_top_level_error(self, mock_current_app):
        with main.app.test_request_context():
            g.requests = MagicMock()
            response = MagicMock()
            response.status_code = 500

            g.requests.get.return_value = response

            self.assertRaises(ApplicationError, CategoryService.get_categories)
            g.requests.get.assert_called_with("{}/categories".format('abc'))
            mock_current_app.logger.info.assert_called()

    @patch('maintain_frontend.dependencies.maintain_api.categories.MAINTAIN_API_URL', 'abc')
    @patch('maintain_frontend.dependencies.maintain_api.categories.current_app')
    def test_get_category_info(self, mock_current_app):
        with main.app.test_request_context():
            g.requests = MagicMock()
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = {
                "permission": None,
                "display-name": "Test 1",
                "name": "test-1",
                "sub-categories": [
                    {"name": "sub name",
                     "display-name": "sub display",
                     "permission": None}
                ],
                "statutory-provisions": [
                    "test stat prov"
                ],
                "instruments": [
                    "test instrument"
                ],
                "parent": None}

            g.requests.get.return_value = response

            category = CategoryService.get_category_parent_info("test")

            self.assertIsNotNone(category)
            self.assertEqual("test-1", category.name)
            self.assertEqual("Test 1", category.display_name)
            self.assertEqual(1, len(category.sub_categories))
            self.assertEqual("sub name", category.sub_categories[0].name)
            self.assertEqual("sub display", category.sub_categories[0].display_name)
            self.assertEqual(1, len(category.statutory_provisions))
            self.assertEqual("test stat prov", category.statutory_provisions[0])
            self.assertEqual(1, len(category.instruments))
            self.assertEqual("test instrument", category.instruments[0])
            self.assertIsNone(category.parent)

            g.requests.get.assert_called_with("{}/categories/test".format('abc'))
            mock_current_app.logger.info.assert_called()

    @patch('maintain_frontend.dependencies.maintain_api.categories.MAINTAIN_API_URL', 'abc')
    @patch('maintain_frontend.dependencies.maintain_api.categories.current_app')
    def test_get_category_info_permission_filtered(self, mock_current_app):
        with main.app.test_request_context():
            g.requests = MagicMock()
            g.session = MagicMock()
            g.session.user.permissions = []
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = {
                "permission": None,
                "display-name": "Test 1",
                "name": "test-1",
                "sub-categories": [
                    {"name": "sub name",
                     "display-name": "sub display",
                     "permission": "abc"}
                ],
                "statutory-provisions": [
                    "test stat prov"
                ],
                "instruments": [
                    "test instrument"
                ],
                "parent": None}

            g.requests.get.return_value = response

            category = CategoryService.get_category_parent_info("test")

            self.assertIsNotNone(category)
            self.assertEqual("test-1", category.name)
            self.assertEqual("Test 1", category.display_name)
            self.assertEqual(0, len(category.sub_categories))
            self.assertEqual(1, len(category.statutory_provisions))
            self.assertEqual("test stat prov", category.statutory_provisions[0])
            self.assertEqual(1, len(category.instruments))
            self.assertEqual("test instrument", category.instruments[0])
            self.assertIsNone(category.parent)

            g.requests.get.assert_called_with("{}/categories/test".format('abc'))
            mock_current_app.logger.info.assert_called()

    @patch('maintain_frontend.dependencies.maintain_api.categories.MAINTAIN_API_URL', 'abc')
    @patch('maintain_frontend.dependencies.maintain_api.categories.current_app')
    def test_get_category_info_permission(self, mock_current_app):
        with main.app.test_request_context():
            g.requests = MagicMock()
            g.session = MagicMock()
            g.session.user.permissions = ["parent-permission", "sub-permission"]
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = {
                "permission": "parent-permission",
                "display-name": "Test 1",
                "name": "test-1",
                "sub-categories": [
                    {"name": "sub name",
                     "display-name": "sub display",
                     "permission": "sub-permission"}
                ],
                "statutory-provisions": [
                    "test stat prov"
                ],
                "instruments": [
                    "test instrument"
                ],
                "parent": None}

            g.requests.get.return_value = response

            category = CategoryService.get_category_parent_info("test")

            self.assertIsNotNone(category)
            self.assertEqual("test-1", category.name)
            self.assertEqual("Test 1", category.display_name)
            self.assertEqual(1, len(category.sub_categories))
            self.assertEqual("sub name", category.sub_categories[0].name)
            self.assertEqual("sub display", category.sub_categories[0].display_name)
            self.assertEqual(1, len(category.statutory_provisions))
            self.assertEqual("test stat prov", category.statutory_provisions[0])
            self.assertEqual(1, len(category.instruments))
            self.assertEqual("test instrument", category.instruments[0])

            g.requests.get.assert_called_with("{}/categories/test".format('abc'))
            mock_current_app.logger.info.assert_called()

    @patch('maintain_frontend.dependencies.maintain_api.categories.MAINTAIN_API_URL', 'abc')
    @patch('maintain_frontend.dependencies.maintain_api.categories.current_app')
    def test_get_category_info_error(self, mock_current_app):
        with main.app.test_request_context():
            g.requests = MagicMock()
            response = MagicMock()
            response.status_code = 500

            g.requests.get.return_value = response

            self.assertRaises(ApplicationError, CategoryService.get_category_parent_info, "test")
            g.requests.get.assert_called_with("{}/categories/test".format('abc'))
            mock_current_app.logger.info.assert_called()

    @patch('maintain_frontend.dependencies.maintain_api.categories.MAINTAIN_API_URL', 'abc')
    @patch('maintain_frontend.dependencies.maintain_api.categories.current_app')
    def test_get_sub_category_info(self, mock_current_app):
        with main.app.test_request_context():
            g.requests = MagicMock()
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = {
                "permission": None,
                "display-name": "Test 1",
                "name": "test-1",
                "sub-categories": [
                    {"name": "sub name",
                     "display-name": "sub display",
                     "permission": None}
                ],
                "statutory-provisions": [
                    "test stat prov"
                ],
                "instruments": [
                    "test instrument"
                ],
                "parent": None}

            g.requests.get.return_value = response

            category = CategoryService.get_sub_category_info("test", "parent")

            self.assertIsNotNone(category)
            self.assertEqual("test-1", category.name)
            self.assertEqual("Test 1", category.display_name)
            self.assertEqual(1, len(category.sub_categories))
            self.assertEqual("sub name", category.sub_categories[0].name)
            self.assertEqual("sub display", category.sub_categories[0].display_name)
            self.assertEqual(1, len(category.statutory_provisions))
            self.assertEqual("test stat prov", category.statutory_provisions[0])
            self.assertEqual(1, len(category.instruments))
            self.assertEqual("test instrument", category.instruments[0])
            self.assertIsNone(category.parent)

            g.requests.get.assert_called_with("{}/categories/test/sub-categories/parent".format('abc'))
            mock_current_app.logger.info.assert_called()

    @patch('maintain_frontend.dependencies.maintain_api.categories.MAINTAIN_API_URL', 'abc')
    @patch('maintain_frontend.dependencies.maintain_api.categories.current_app')
    def test_get_sub_category_info_permission_filtered(self, mock_current_app):
        with main.app.test_request_context():
            g.requests = MagicMock()
            g.session = MagicMock()
            g.session.user.permissions = []
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = {
                "permission": None,
                "display-name": "Test 1",
                "name": "test-1",
                "sub-categories": [
                    {"name": "sub name",
                     "display-name": "sub display",
                     "permission": "abc"}
                ],
                "statutory-provisions": [
                    "test stat prov"
                ],
                "instruments": [
                    "test instrument"
                ],
                "parent": None}

            g.requests.get.return_value = response

            category = CategoryService.get_sub_category_info("test", "abc")

            self.assertIsNotNone(category)
            self.assertEqual("test-1", category.name)
            self.assertEqual("Test 1", category.display_name)
            self.assertEqual(0, len(category.sub_categories))
            self.assertEqual(1, len(category.statutory_provisions))
            self.assertEqual("test stat prov", category.statutory_provisions[0])
            self.assertEqual(1, len(category.instruments))
            self.assertEqual("test instrument", category.instruments[0])
            self.assertIsNone(category.parent)

            g.requests.get.assert_called_with("{}/categories/test/sub-categories/abc".format('abc'))
            mock_current_app.logger.info.assert_called()

    @patch('maintain_frontend.dependencies.maintain_api.categories.MAINTAIN_API_URL', 'abc')
    @patch('maintain_frontend.dependencies.maintain_api.categories.current_app')
    def test_get_sub_category_info_permission(self, mock_current_app):
        with main.app.test_request_context():
            g.requests = MagicMock()
            g.session = MagicMock()
            g.session.user.permissions = ["parent-permission", "sub-permission"]
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = {
                "permission": "parent-permission",
                "display-name": "Test 1",
                "name": "test-1",
                "sub-categories": [
                    {"name": "sub name",
                     "display-name": "sub display",
                     "permission": "sub-permission"}
                ],
                "statutory-provisions": [
                    "test stat prov"
                ],
                "instruments": [
                    "test instrument"
                ],
                "parent": None}

            g.requests.get.return_value = response

            category = CategoryService.get_sub_category_info("test", "abc")

            self.assertIsNotNone(category)
            self.assertEqual("test-1", category.name)
            self.assertEqual("Test 1", category.display_name)
            self.assertEqual(1, len(category.sub_categories))
            self.assertEqual("sub name", category.sub_categories[0].name)
            self.assertEqual("sub display", category.sub_categories[0].display_name)
            self.assertEqual(1, len(category.statutory_provisions))
            self.assertEqual("test stat prov", category.statutory_provisions[0])
            self.assertEqual(1, len(category.instruments))
            self.assertEqual("test instrument", category.instruments[0])

            g.requests.get.assert_called_with("{}/categories/test/sub-categories/abc".format('abc'))
            mock_current_app.logger.info.assert_called()

    @patch('maintain_frontend.dependencies.maintain_api.categories.MAINTAIN_API_URL', 'abc')
    @patch('maintain_frontend.dependencies.maintain_api.categories.current_app')
    def test_get_sub_category_info_error(self, mock_current_app):
        with main.app.test_request_context():
            g.requests = MagicMock()
            response = MagicMock()
            response.status_code = 500

            g.requests.get.return_value = response

            self.assertRaises(ApplicationError, CategoryService.get_sub_category_info, "test", "abc")
            g.requests.get.assert_called_with("{}/categories/test/sub-categories/abc".format('abc'))
            mock_current_app.logger.info.assert_called()

    @patch('maintain_frontend.dependencies.maintain_api.categories.MAINTAIN_API_URL', 'abc')
    @patch('maintain_frontend.dependencies.maintain_api.categories.current_app')
    def test_get_all_stat_provs(self, mock_current_app):
        with main.app.test_request_context():
            g.requests = MagicMock()
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = ["test stat prov"]

            g.requests.get.return_value = response

            stat_provs = CategoryService.get_all_stat_provs()

            self.assertIsNotNone(stat_provs)
            self.assertEqual(1, len(stat_provs))
            self.assertEqual("test stat prov", stat_provs[0])

            g.requests.get.assert_called_with("{}/statutory-provisions".format('abc'),
                                              params={'selectable': True})
            mock_current_app.logger.info.assert_called()

    @patch('maintain_frontend.dependencies.maintain_api.categories.MAINTAIN_API_URL', 'abc')
    @patch('maintain_frontend.dependencies.maintain_api.categories.current_app')
    def test_get_all_stat_provs_error(self, mock_current_app):
        with main.app.test_request_context():
            g.requests = MagicMock()
            response = MagicMock()
            response.status_code = 500

            g.requests.get.return_value = response

            self.assertRaises(ApplicationError, CategoryService.get_all_stat_provs)
            g.requests.get.assert_called_with("{}/statutory-provisions".format('abc'),
                                              params={'selectable': True})
            mock_current_app.logger.info.assert_called()

    @patch('maintain_frontend.dependencies.maintain_api.categories.MAINTAIN_API_URL', 'abc')
    @patch('maintain_frontend.dependencies.maintain_api.categories.current_app')
    def test_get_all_instruments(self, mock_current_app):
        with main.app.test_request_context():
            g.requests = MagicMock()
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = ["test instrument"]

            g.requests.get.return_value = response

            instruments = CategoryService.get_all_instruments()

            self.assertIsNotNone(instruments)
            self.assertEqual(1, len(instruments))
            self.assertEqual("test instrument", instruments[0])

            g.requests.get.assert_called_with("abc/instruments")
            mock_current_app.logger.info.assert_called()

    @patch('maintain_frontend.dependencies.maintain_api.categories.MAINTAIN_API_URL', 'abc')
    @patch('maintain_frontend.dependencies.maintain_api.categories.current_app')
    def test_get_all_instruments_error(self, mock_current_app):
        with main.app.test_request_context():
            g.requests = MagicMock()
            response = MagicMock()
            response.status_code = 500

            g.requests.get.return_value = response

            self.assertRaises(ApplicationError, CategoryService.get_all_instruments)
            g.requests.get.assert_called_with("{}/instruments".format('abc'))
            mock_current_app.logger.info.assert_called()
