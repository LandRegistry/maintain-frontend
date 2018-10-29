from unittest import TestCase
from unit_tests.utilities import Utilities
from unittest.mock import MagicMock
from flask import g
from maintain_frontend import main
from maintain_frontend.dependencies.report_api.report_api_service import ReportAPIService


BASE64_BOUNDING_BOX = "eyJjb29yZGluYXRlcyI6WzQ0ODY4MS41Mzc1MDAwMDAwMywyNzk2NTkuMTEyNV0sInR5cGUiOiJQb2ludCJ9"


class TestReportAPIService(TestCase):
    def setUp(self):
        self.app = main.app.test_client()
        Utilities.mock_session_cookie_unittest(self)

    def test_send_number_of_charges_per_search_data(self):
        with main.app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = '333'
            response = MagicMock()
            response.status_code = 200
            response.text = "Adding data to charges_per_search_report_data table"
            g.requests.post.return_value = response

            report_data = {
                "date": "2018-07-23 12:47:12.591905",
                "channel": "MAINTAIN",
                "number_of_charges": 10,
                "repeat": False
            }

            response = ReportAPIService.send_number_of_charges_per_search_data(report_data)

            args_tuple, kwargs = g.requests.post.call_args
            url_called, = args_tuple
            self.assertIn('number-of-charges-per-search', url_called)
            g.requests.post.assert_called_with(
                url_called,
                json=report_data,
                headers={'Content-Type': 'application/json'})
            self.assertEqual(200, response.status_code)

    def test_exception_handled(self):
        with main.app.test_request_context():
            g.trace_id = '333'
            g.session = MagicMock()
            g.requests = MagicMock()
            g.requests.post.side_effect = Exception("Test exception")

            report_data = MagicMock()
            response = ReportAPIService.send_number_of_charges_per_search_data(report_data)
            self.assertEqual(500, response.status_code)
