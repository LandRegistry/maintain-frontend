import datetime

from maintain_frontend import main
from flask_testing import TestCase
from unit_tests.utilities import Utilities
from flask import url_for, g
from unittest.mock import patch
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.models import LightObstructionNoticeItem
from dateutil.relativedelta import relativedelta
from io import BytesIO

TEMPLATE = 'upload_lon_documents.html'

ADD_LON = 'add_lon.'
GET_UPLOAD_LON_DOCUMENTS = ADD_LON + 'get_upload_lon_documents'
POST_UPLOAD_LON_DOCUMENTS = ADD_LON + 'post_upload_lon_documents'
GET_SERVIENT_STRUCTURE_HEIGHT = ADD_LON + 'get_servient_structure_height'

NO_VALIDATION_ERRORS = []


class TestLONUploadLonDocuments(TestCase):

    def create_app(self):
        main.app.testing = True
        Utilities.mock_session_cookie_flask_test(self)
        return main.app

    def test_upload_lon_documents_redirects_to_new_when_state_none(self):
        self.client.set_cookie('localhost', Session.session_cookie_name,
                               'cookie_value')

        self.mock_session.return_value.add_lon_charge_state = None
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        response = self.client.get(url_for(GET_UPLOAD_LON_DOCUMENTS))

        self.assert_status(response, 302)
        self.assertRedirects(response, url_for(ADD_LON + 'new'))

    def test_upload_lon_documents_get(self):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LightObstructionNoticeItem()
        self.mock_session.add_lon_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]

        response = self.client.get(url_for(GET_UPLOAD_LON_DOCUMENTS))

        self.assert_status(response, 200)
        self.assert_template_used(TEMPLATE)

    @patch('maintain_frontend.add_lon.upload_lon_documents.UploadLonDocumentsValidator')
    def test_upload_lon_documents_no_select(self, mock_validator):
        self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

        state = LightObstructionNoticeItem()
        self.mock_session.add_lon_charge_state = state
        self.mock_session.return_value.user.permissions = [Permissions.add_lon]
        mock_validator.validate.return_value.errors = {'certificate': ['Choose one']}

        response = self.client.post(url_for(POST_UPLOAD_LON_DOCUMENTS))

        self.assert_context('validation_errors', {'certificate': ['Choose one']})
        self.assert_status(response, 400)
        self.assert_template_used(TEMPLATE)

    @patch('maintain_frontend.add_lon.upload_lon_documents.ReviewRouter')
    @patch('maintain_frontend.add_lon.upload_lon_documents.UploadLonDocumentsValidator')
    @patch('maintain_frontend.add_lon.upload_lon_documents.upload_lon_docs')
    def test_upload_lon_documents_no_errors(self, mock_upload_func, mock_validator, mock_review_router):
        with main.app.test_request_context():
            self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')

            mock_review_router.get_redirect_url.return_value = url_for(GET_SERVIENT_STRUCTURE_HEIGHT)
            expected_filenames = {
                "form_a": 'test1.pdf',
                "temporary_lon_cert": 'test2.pdf',
                "definitive_lon_cert": 'test3.pdf'
            }

            state = LightObstructionNoticeItem()
            self.mock_session.add_lon_charge_state = state
            self.mock_session.return_value.user.permissions = [Permissions.add_lon]

            mock_validator.validate.return_value.errors = None

            response = self.client.post(url_for(POST_UPLOAD_LON_DOCUMENTS),
                                        buffered=True,
                                        content_type='multipart/form-data',
                                        data=dict({
                                            'form-a-file-input': (BytesIO(b'a'), 'test1.pdf'),
                                            'temporary-lon-cert-file-input': (BytesIO(b'a'), 'test2.pdf'),
                                            'definitive-lon-cert-file-input': (BytesIO(b'a'), 'test3.pdf'),
                                            'certificate': ['Definitive LON certificate', 'Temporary LON certificate'],
                                            'definitive_cert_year': '2012',
                                            'definitive_cert_month': '12',
                                            'definitive_cert_day': '24',
                                            'temp_cert_year': '2003',
                                            'temp_cert_month': '2',
                                            'temp_cert_day': '1',
                                            'temp_expiry_year': '2006',
                                            'temp_expiry_month': '5',
                                            'temp_expiry_day': '4'
                                        }))

            self.assert_status(response, 302)
            self.assertRedirects(response, url_for(GET_SERVIENT_STRUCTURE_HEIGHT))
            self.assertEqual(self.mock_session.return_value.filenames, expected_filenames)

    @patch('maintain_frontend.add_lon.upload_lon_documents.ReviewRouter')
    @patch('maintain_frontend.add_lon.upload_lon_documents.UploadLonDocumentsValidator')
    @patch('maintain_frontend.add_lon.upload_lon_documents.upload_lon_docs')
    def test_definitive_expiry_automatically_set_to_21_years_after_valid_from(self,
                                                                              mock_upload_func,
                                                                              mock_validator,
                                                                              mock_review_router):
        with main.app.test_request_context():
            self.client.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
            valid_from = datetime.date.today()
            expected_expiry_date = valid_from + relativedelta(years=+21)

            mock_review_router.get_redirect_url.return_value = url_for(GET_SERVIENT_STRUCTURE_HEIGHT)
            expected_filenames = {
                "form_a": 'test1.pdf',
                "temporary_lon_cert": 'test2.pdf',
                "definitive_lon_cert": 'test3.pdf'
            }

            state = LightObstructionNoticeItem()

            self.mock_session.add_lon_charge_state = state
            self.mock_session.return_value.user.permissions = [Permissions.add_lon]
            mock_validator.validate.return_value.errors = None

            response = self.client.post(url_for(POST_UPLOAD_LON_DOCUMENTS),
                                        buffered=True,
                                        content_type='multipart/form-data',
                                        data=dict({
                                            'form-a-file-input': (BytesIO(b'a'), 'test1.pdf'),
                                            'temporary-lon-cert-file-input': (BytesIO(b'a'), 'test2.pdf'),
                                            'definitive-lon-cert-file-input': (BytesIO(b'a'), 'test3.pdf'),
                                            'certificate': ['Definitive LON certificate', 'Temporary LON certificate'],
                                            'definitive_cert_year': '2012',
                                            'definitive_cert_month': '12',
                                            'definitive_cert_day': '24',
                                            'temp_cert_year': '2003',
                                            'temp_cert_month': '2',
                                            'temp_cert_day': '1',
                                            'temp_expiry_year': '2006',
                                            'temp_expiry_month': '5',
                                            'temp_expiry_day': '4'
                                        }))

            self.assert_status(response, 302)
            self.assertRedirects(response, url_for(GET_SERVIENT_STRUCTURE_HEIGHT))
            self.assertEqual(g.session.add_lon_charge_state.expiry_date, expected_expiry_date)
            self.assertEqual(g.session.filenames, expected_filenames)
