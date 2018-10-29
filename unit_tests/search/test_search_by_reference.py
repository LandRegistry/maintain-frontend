from unittest.mock import Mock, patch
from flask_testing import TestCase
from flask import url_for
from maintain_frontend import main
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.dependencies.session_api.session import Session
from unit_tests.utilities import Utilities

test_json_result = [{'item': {
    'amount-originally-secured': 'an amount',
    'charge-creation-date': '2011-01-01',
    'charge-geographic-description': 'a description',
    'charge-type': 'a charge type',
    'end-date': '2011-01-01',
    'expiry-date': '2011-01-01',
    'further-information-location': 'a location',
    'further-information-reference': 'a reference',
    'instrument': 'An instrument',
    'land-capacity-description': 'a description',
    'land-compensation-paid': 'compensation',
    'land-works-particulars': 'particulars',
    'local-land-charge': 1,
    'migrating-authority': 'another authority',
    'migration-supplier': 'a supplier',
    'old-register-part': '1a',
    'originating-authority': 'an authority',
    'rate-of-interest': 'a rate',
    'registration-date': '2011-01-01',
    'start-date': '2011-01-01',
    'statutory-provision': 'a provision',
    'originating-authority-charge-identifier': 'an identifier',
    'unique-property-reference-numbers': [123, 456]
}}]


class TestSearchByReference(TestCase):
    SEARCH_PATH = 'maintain_frontend.search.search_by_reference'

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_get_search_by_reference_success(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.user.permissions = [Permissions.browse_llc]
        self.mock_session.return_value.commit = Mock()

        response = self.client.get(url_for('search.get_search_by_reference'))

        self.assert200(response)
        self.assert_template_used('search-by-reference.html')

    @patch("{}.ReferenceValidator".format(SEARCH_PATH))
    @patch("{}.SearchByReference".format(SEARCH_PATH))
    def test_post_search_by_reference_trailing_whitespace_success(
        self,
        mock_search_by_reference,
        mock_reference_validator
    ):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.user.permissions = [Permissions.browse_llc]
        self.mock_session.return_value.commit = Mock()

        mock_validation_return_object = Mock()
        mock_validation_return_object.errors = None
        mock_reference_validator.validate.return_value = mock_validation_return_object

        mock_response = {'status_code': 200, 'results': test_json_result}

        mock_search_by_reference.return_value.process.return_value = mock_response

        # Test that trailing whitespace is stripped from the reference
        response = self.client.post(
            url_for('search.post_search_by_reference'),
            data={'search-reference': ' LLC-1 '}
        )

        mock_search_by_reference.return_value.process.assert_called_with('LLC-1')
        self.assertRedirects(response, url_for('view_land_charge.view_land_charge', local_land_charge='LLC-1'))
