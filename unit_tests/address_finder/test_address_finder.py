from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from maintain_frontend.dependencies.session_api.session import Session
import mock
import json
from requests.models import Response


class TestAddressFinder(TestCase):

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    @mock.patch("maintain_frontend.address_finder.address_finder.AddressesService")
    @mock.patch("maintain_frontend.address_finder.address_finder.request")
    def test_get_addresses_valid_postcode(self,
                                          mock_request,
                                          mock_addresses_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        mock_request.args.get.return_value = "EX4 7AN"
        mock_request.is_xhr.return_value = True
        mock_content = [{"address": "1 main road"}]

        mock_response = Response()
        mock_response.status_code = 200
        mock_response._content = json.dumps(mock_content).encode()
        mock_addresses_service.return_value.get_by.return_value = mock_response

        response = self.client.get("/address-finder/_search")

        response_object = json.loads(response.data.decode())
        self.assertEqual([{"address": "1 main road"}], response_object['addresses'])

    @mock.patch("maintain_frontend.address_finder.address_finder.request")
    def test_get_addresses_invalid_postcode(self,
                                            mock_request):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        mock_request.args.get.return_value = "EX4N"
        mock_request.is_xhr.return_value = True

        response = self.client.get("/address-finder/_search")

        response_object = json.loads(response.data.decode())
        self.assertEqual("Invalid postcode, please try again", response_object['search_postcode_message'])

    @mock.patch("maintain_frontend.address_finder.address_finder.request")
    def test_get_addresses_missing_postcode(self,
                                            mock_request):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        mock_request.args.get.return_value = None
        mock_request.is_xhr.return_value = True

        response = self.client.get("/address-finder/_search")

        response_object = json.loads(response.data.decode())
        self.assertEqual("Enter postcode or choose 'Enter address manually'",
                         response_object['search_postcode_message'])
        self.assertEqual("Enter postcode or choose 'Enter address manually'",
                         response_object['search_postcode_message'])

    @mock.patch("maintain_frontend.address_finder.address_finder.AddressesService")
    @mock.patch("maintain_frontend.address_finder.address_finder.request")
    def test_get_addresses_valid_postcode_not_found(self,
                                                    mock_request,
                                                    mock_addresses_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        mock_request.args.get.return_value = "EX4 7AN"
        mock_request.is_xhr.return_value = True

        mock_response = Response()
        mock_response.status_code = 404

        mock_addresses_service.return_value.get_by.return_value = mock_response

        response = self.client.get("/address-finder/_search")

        response_object = json.loads(response.data.decode())
        self.assertEqual("Results not found. Try another search", response_object['search_postcode_message'])
        self.assertEqual("Results not found. Try another search", response_object['search_message_inline_message'])

    @mock.patch("maintain_frontend.address_finder.address_finder.AddressesService")
    @mock.patch("maintain_frontend.address_finder.address_finder.request")
    def test_get_addresses_invalid_postcode_valid_format(self,
                                                         mock_request,
                                                         mock_addresses_service):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        mock_request.args.get.return_value = "AB1 2CD"
        mock_request.is_xhr.return_value = True

        mock_response = Response()
        mock_response.status_code = 400

        mock_addresses_service.return_value.get_by.return_value = mock_response

        response = self.client.get("/address-finder/_search")

        response_object = json.loads(response.data.decode())
        self.assertEqual("Invalid postcode, please try again", response_object['search_postcode_message'])
        self.assertEqual("Invalid postcode, please try again", response_object['search_message_inline_message'])
