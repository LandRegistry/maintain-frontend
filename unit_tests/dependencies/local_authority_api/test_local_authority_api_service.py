from maintain_frontend.dependencies.local_authority_api.local_authority_api_service import LocalAuthorityService
from maintain_frontend.exceptions import ApplicationError
from unittest import TestCase
from unittest.mock import patch, MagicMock
from maintain_frontend import main
from unit_tests.utilities import Utilities
from flask import g
import json


PATH = 'maintain_frontend.dependencies.local_authority_api.local_authority_api_service'

ORIGINATING_AUTHORITIES = [
    'Authority A',
    'Authority B',
    'Authority C',
    'Authority D',
]


class TestLocalAuthorityApiService(TestCase):

    def setUp(self):
        self.app = main.app.test_client()
        Utilities.mock_session_cookie_unittest(self)

    @patch('{}.current_app'.format(PATH))
    def test_get_get_bounding_box_success(self, mock_current_app):
        with main.app.test_request_context():
            g.requests = MagicMock()
            local_authority_name = "Winchester District (B)"
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = {"geometry":
                                          {"type": "Polygon",
                                           "coordinates": [[[438199.90401036787, 106603.8042336921],
                                                            [438199.90401036787, 144431.39619812733],
                                                            [468030.1970266425, 144431.39619812733],
                                                            [468030.1970266425, 106603.8042336921],
                                                            [438199.90401036787, 106603.8042336921]]]
                                           },
                                          "type": "Feature",
                                          "properties": {"local-authority-name": local_authority_name}
                                          }

            g.requests.get.return_value = response
            la_api_url = "http://localhost:8080"
            mock_current_app.config = {'LA_API_URL': la_api_url}

            local_authority_service = LocalAuthorityService(mock_current_app.config)
            response = local_authority_service.get_bounding_box("Winchester District (B)")
            self.assertEqual(response.status_code, 200)

            g.requests.get.assert_called_with(
                "{}/v1.0/local-authorities/{}/bounding_box".format(la_api_url, local_authority_name)
            )

    @patch('{}.current_app'.format(PATH))
    def test_get_originating_authorities_success(self, mock_current_app):
        with main.app.test_request_context():
            g.requests = MagicMock()
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = ORIGINATING_AUTHORITIES

            g.requests.get.return_value = response
            la_api_url = "http://localhost:8080"
            mock_current_app.config = {'LA_API_URL': la_api_url}

            local_authority_service = LocalAuthorityService(mock_current_app.config)
            response = local_authority_service.get_organisations()
            self.assertEqual(response, ORIGINATING_AUTHORITIES)

            g.requests.get.assert_called_with("{}/v1.0/organisations".format(la_api_url))

    @patch('{}.current_app'.format(PATH))
    def test_get_authorities_by_extent_success(self, mock_current_app):
        with main.app.test_request_context():
            g.requests = MagicMock()
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = {"abc": True, "def": False}

            g.requests.post.return_value = response
            la_api_url = "ABC"
            mock_current_app.config = {'LA_API_URL': la_api_url}

            local_authority_service = LocalAuthorityService(mock_current_app.config)
            response = local_authority_service.get_authorities_by_extent({"test": "test"})
            self.assertEqual(response, {"abc": True, "def": False})

            g.requests.post.assert_called_with("{}/v1.0/local-authorities".format(la_api_url),
                                               data='{"test": "test"}', headers={'Content-Type': 'application/json'})

    @patch('{}.current_app'.format(PATH))
    def test_get_authorities_by_extent_no_results(self, mock_current_app):
        with main.app.test_request_context():
            g.requests = MagicMock()
            response = MagicMock()
            response.status_code = 404

            g.requests.post.return_value = response
            la_api_url = "ABC"
            mock_current_app.config = {'LA_API_URL': la_api_url}

            local_authority_service = LocalAuthorityService(mock_current_app.config)

            response = local_authority_service.get_authorities_by_extent({"test": "test"})
            self.assertEqual(response, {})

            g.requests.post.assert_called_with("{}/v1.0/local-authorities".format(la_api_url),
                                               data='{"test": "test"}', headers={'Content-Type': 'application/json'})

    @patch('{}.current_app'.format(PATH))
    def test_get_authorities_by_extent_exception(self, mock_current_app):
        with main.app.test_request_context():
            g.requests = MagicMock()
            response = MagicMock()
            response.status_code = 500
            response.json.return_value = {"abc": True, "def": False}

            g.requests.post.return_value = response
            la_api_url = "ABC"
            mock_current_app.config = {'LA_API_URL': la_api_url}

            local_authority_service = LocalAuthorityService(mock_current_app.config)

            self.assertRaises(ApplicationError, local_authority_service.get_authorities_by_extent, {"test": "test"})

            g.requests.post.assert_called_with("{}/v1.0/local-authorities".format(la_api_url),
                                               data='{"test": "test"}', headers={'Content-Type': 'application/json'})

    @patch('{}.current_app'.format(PATH))
    def test_is_extent_within_migrated_area_200_result(self, mock_current_app):
        with main.app.test_request_context():
            expected_result = True

            response = MagicMock()
            response.status_code = 200
            response.json.return_value = expected_result

            g.requests = MagicMock()
            g.requests.post.return_value = response

            some_input = {"test": "test"}
            some_url = "some_url"
            mock_current_app.config = {'LA_API_URL': some_url}

            local_authority_service = LocalAuthorityService(mock_current_app.config)
            response = local_authority_service.is_extent_within_migrated_area(some_input)

            self.assertEqual(response, expected_result)

            g.requests.post.assert_called_with(
                "{}/v1.0/local-authorities/is_extent_within_migrated_area".format(some_url),
                data=some_input,
                headers={'Content-Type': 'application/json'}
            )

    @patch('{}.current_app'.format(PATH))
    def test_is_extent_within_migrated_area_500_result(self, mock_current_app):
        with main.app.test_request_context():
            response = MagicMock()
            response.status_code = 500

            g.requests = MagicMock()
            g.requests.post.return_value = response

            some_input = {"test": "test"}
            some_url = "some_url"
            mock_current_app.config = {'LA_API_URL': some_url}

            local_authority_service = LocalAuthorityService(mock_current_app.config)

            self.assertRaises(ApplicationError, local_authority_service.is_extent_within_migrated_area, some_input)

            g.requests.post.assert_called_with(
                "{}/v1.0/local-authorities/is_extent_within_migrated_area".format(some_url),
                data=some_input,
                headers={'Content-Type': 'application/json'}
            )

    @patch('{}.current_app'.format(PATH))
    def test_get_organisation_source_information_success(self, mock_current_app):
        with main.app.test_request_context():
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = [{"source-information": "test"}]

            g.requests = MagicMock()
            g.requests.get.return_value = response

            la_api_url = "http://test-url"
            mock_current_app.config = {'LA_API_URL': la_api_url}

            local_authority_service = LocalAuthorityService(mock_current_app.config)
            response = local_authority_service.get_source_information_for_organisation("Test Organisation")

            self.assertEqual(response, [{"source-information": "test"}])
            g.requests.get.assert_called_with("{}/v1.0/organisations/Test Organisation/source-information"
                                              .format(la_api_url))

    @patch('{}.current_app'.format(PATH))
    def test_get_organisation_source_information_fail(self, mock_current_app):
        with main.app.test_request_context():
            response = MagicMock()
            response.status_code = 500

            g.requests = MagicMock()
            g.requests.get.return_value = response

            local_authority_service = LocalAuthorityService(mock_current_app.config)
            with self.assertRaises(ApplicationError):
                local_authority_service.get_source_information_for_organisation("Test Organisation")

    @patch('{}.current_app'.format(PATH))
    def test_add_organisation_source_information_success(self, mock_current_app):
        with main.app.test_request_context():
            response = MagicMock()
            response.status_code = 201
            response.json.return_value = [{"source-information": "test"}]

            g.requests = MagicMock()
            g.requests.post.return_value = response

            la_api_url = "http://test-url"
            mock_current_app.config = {'LA_API_URL': la_api_url}

            local_authority_service = LocalAuthorityService(mock_current_app.config)
            response = local_authority_service.add_source_information_for_organisation("Test Source",
                                                                                       "Test Organisation")

            self.assertEqual(response, [{"source-information": "test"}])
            g.requests.post.assert_called_with("{}/v1.0/organisations/Test Organisation/source-information".
                                               format(la_api_url),
                                               data=json.dumps({"source-information": "Test Source"}),
                                               headers={'Content-Type': 'application/json'})

    @patch('{}.current_app'.format(PATH))
    def test_add_organisation_source_information_fail(self, mock_current_app):
        with main.app.test_request_context():
            response = MagicMock()
            response.status_code = 500

            g.requests = MagicMock()
            g.requests.post.return_value = response

            local_authority_service = LocalAuthorityService(mock_current_app.config)
            with self.assertRaises(ApplicationError):
                local_authority_service.add_source_information_for_organisation("Test Source", "Test Organisation")
