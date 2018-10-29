from unittest import TestCase
from flask import g
from unittest.mock import MagicMock
from maintain_frontend import main
from unit_tests.utilities import Utilities
from maintain_frontend.dependencies.session_api.user import User
from maintain_frontend.dependencies.storage_api.storage_api_service import StorageAPIService
from maintain_frontend.exceptions import ApplicationError

STORAGE_API_SERVICE_PATH = 'maintain_frontend.dependencies.storage_api.storage_api_service'


class TestStorageApiService(TestCase):
    MOCK_STORAGE_API_URL = 'mock_url'

    def setUp(self):
        self.app = main.app.test_client()
        Utilities.mock_session_cookie_unittest(self)

    def setup_common_mocks(self):
        g.requests = MagicMock()
        g.trace_id = '123'
        g.session = self.mock_session

        user = User()
        user.email = "abc"
        self.mock_session = user

    def setup_response_mock(self, status_code, json_return_value):
        response = MagicMock()
        response.status_code = status_code
        response.json.return_value = json_return_value

        return response

    def setup_storage_api_service(self):
        config = {'STORAGE_API_URL': self.MOCK_STORAGE_API_URL}
        storage_api_service = StorageAPIService(config)

        return storage_api_service

    def test_post_save_file_success(self):
        with main.app.test_request_context():
            mock_bucket = "test_bucket"

            self.setup_common_mocks()
            response = self.setup_response_mock(201, {
                "file": [{"bucket": mock_bucket, "file_id": "07f560a3-18ba-44e9-8133-8027b43f3def"}]
            })
            g.requests.post.return_value = response
            storage_api_service = self.setup_storage_api_service()

            storage_api_service.save_files(files="file", bucket=mock_bucket)

            self.assertEqual(g.requests.post.call_count, 1)
            self.assertEqual(response.status_code, 201)
            g.requests.post.assert_called_with("{}/{}".format(self.MOCK_STORAGE_API_URL, mock_bucket), files="file",
                                               params={})

    def test_post_save_file_with_subdirectories_and_scan(self):
        with main.app.test_request_context():
            mock_bucket = "test_bucket"

            self.setup_common_mocks()
            response = self.setup_response_mock(201, {
                "file": [{"bucket": mock_bucket, "file_id": "07f560a3-18ba-44e9-8133-8027b43f3def"}]
            })
            g.requests.post.return_value = response
            storage_api_service = self.setup_storage_api_service()

            storage_api_service.save_files(files="file", bucket=mock_bucket, subdirectories='test', scan=True)

            self.assertEqual(g.requests.post.call_count, 1)
            self.assertEqual(response.status_code, 201)
            g.requests.post.assert_called_with("{}/{}".format(self.MOCK_STORAGE_API_URL, mock_bucket), files="file",
                                               params={"subdirectories": 'test', "scan": True})

    def test_get_external_url_success(self):
        with main.app.test_request_context():
            mock_file_id = 'mock file id'
            mock_bucket = "test_bucket"

            self.setup_common_mocks()
            expected_result = {
                "external_reference": 'mock_report_url'
            }
            response = self.setup_response_mock(200, expected_result)
            g.requests.get.return_value = response
            storage_api_service = self.setup_storage_api_service()

            result = storage_api_service.get_external_url(mock_file_id, mock_bucket)

            self.assertEqual(result, 'mock_report_url')
            g.requests.get.assert_called_with("{}/{}/{}/external-url".format(self.MOCK_STORAGE_API_URL,
                                                                             mock_bucket,
                                                                             mock_file_id), params={})

    def test_get_external_url_success_with_subdirectories(self):
        with main.app.test_request_context():
            mock_file_id = 'mock file id'
            mock_bucket = "test_bucket"

            self.setup_common_mocks()
            expected_result = {
                "external_reference": 'mock_report_url'
            }
            response = self.setup_response_mock(200, expected_result)
            g.requests.get.return_value = response
            storage_api_service = self.setup_storage_api_service()

            result = storage_api_service.get_external_url('mock file id', "test_bucket",
                                                          subdirectories='a subdirectory')

            self.assertEqual(result, 'mock_report_url')
            g.requests.get.assert_called_with("{}/{}/{}/external-url".format(self.MOCK_STORAGE_API_URL,
                                                                             mock_bucket,
                                                                             mock_file_id),
                                              params={'subdirectories': 'a subdirectory'})

    def test_get_external_url_error_404(self):
        with main.app.test_request_context():
            mock_file_id = 'mock file id'
            mock_bucket = "test_bucket"

            self.setup_common_mocks()
            response = self.setup_response_mock(404, None)
            g.requests.get.return_value = response
            storage_api_service = self.setup_storage_api_service()

            result = storage_api_service.get_external_url(mock_file_id, mock_bucket)

            self.assertIsNone(result)

    def test_get_external_url_error_500(self):
        with main.app.test_request_context():
            mock_file_id = 'mock file id'
            mock_bucket = "test_bucket"

            self.setup_common_mocks()
            response = self.setup_response_mock(500, None)
            g.requests.get.return_value = response
            storage_api_service = self.setup_storage_api_service()

            self.assertRaises(ApplicationError, storage_api_service.get_external_url, mock_file_id, mock_bucket)

    def test_get_external_url_from_path_200(self):
        with main.app.test_request_context():
            mock_file_id = 'mock file id'
            mock_bucket = "test_bucket"

            self.setup_common_mocks()
            expected_result = {
                "external_reference": 'mock_report_url'
            }
            response = self.setup_response_mock(200, expected_result)
            g.requests.get.return_value = response
            storage_api_service = self.setup_storage_api_service()

            result = storage_api_service.get_external_url_from_path("{}/{}".format(
                mock_bucket,
                mock_file_id))

            self.assertEqual(result, 'mock_report_url')
            g.requests.get.assert_called_with("{}/{}/{}/external-url".format(self.MOCK_STORAGE_API_URL,
                                                                             mock_bucket,
                                                                             mock_file_id),
                                              params=None)

    def test_get_external_url_from_path_200_with_subdirectory(self):
        with main.app.test_request_context():
            mock_file_id = 'mock file id'
            mock_bucket = "test_bucket"

            self.setup_common_mocks()
            expected_result = {
                "external_reference": 'mock_report_url'
            }
            response = self.setup_response_mock(200, expected_result)
            g.requests.get.return_value = response
            storage_api_service = self.setup_storage_api_service()

            result = storage_api_service.get_external_url_from_path("{}/{}?subdirectories=test".format(
                mock_bucket,
                mock_file_id))

            self.assertEqual(result, 'mock_report_url')
            g.requests.get.assert_called_with("{}/{}/{}/external-url".format(self.MOCK_STORAGE_API_URL,
                                                                             mock_bucket,
                                                                             mock_file_id),
                                              params={'subdirectories': 'test'})

    def test_get_external_url_from_path_404(self):
        with main.app.test_request_context():
            mock_file_id = 'mock file id'
            mock_bucket = "test_bucket"

            self.setup_common_mocks()
            expected_result = {
                "external_reference": 'mock_report_url'
            }
            response = self.setup_response_mock(404, expected_result)
            g.requests.get.return_value = response
            storage_api_service = self.setup_storage_api_service()

            result = storage_api_service.get_external_url_from_path("{}/{}?subdirectories=test".format(
                mock_bucket,
                mock_file_id))

            self.assertIsNone(result)
            g.requests.get.assert_called_with("{}/{}/{}/external-url".format(self.MOCK_STORAGE_API_URL,
                                                                             mock_bucket,
                                                                             mock_file_id),
                                              params={'subdirectories': 'test'})

    def test_get_external_url_from_path_500(self):
        with main.app.test_request_context():
            mock_file_id = 'mock file id'
            mock_bucket = "test_bucket"

            self.setup_common_mocks()
            response = self.setup_response_mock(500, None)
            g.requests.get.return_value = response
            storage_api_service = self.setup_storage_api_service()

            self.assertRaises(ApplicationError,
                              storage_api_service.get_external_url_from_path,
                              "{}/{}?subdirectories=test".format(
                                  mock_bucket,
                                  mock_file_id))
