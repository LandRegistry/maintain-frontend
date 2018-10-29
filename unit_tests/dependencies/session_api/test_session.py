from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.dependencies.session_api.user import User
from maintain_frontend.dependencies.session_api.last_created_charge import LastCreatedCharge
from maintain_frontend.models import LocalLandChargeItem, LightObstructionNoticeItem, LLC1Search, Category
from unittest import TestCase
from unittest.mock import patch
from maintain_frontend import main
from flask import g
from datetime import date


class TestSessionModel(TestCase):

    def create_app(self):
        return main.app

    def test_initialisation(self):
        sess = Session('abc')
        self.assertIsNotNone(sess)
        self.assertEqual(sess.session_key, 'abc')

    def test_value_set(self):
        search_extent_geo = {
            'features': [
                {
                    'geometry': {
                        'coordinates': [[
                            [-378838.7455502291, 6966202.685233321],
                            [159887.69930341933, 6965138.008464836],
                            [177987.20436767233, 6568013.573819755],
                            [-456560.1496496685, 6562690.189977327],
                            [-378838.7455502291, 6966202.685233321]
                        ]]
                    }
                }
            ]
        }

        category_obj = Category(name="top-level",
                                display_name="Top Level",
                                sub_categories=[],
                                parent=None,
                                statutory_provisions=[],
                                instruments=[])

        add_lon_charge_state_obj = LightObstructionNoticeItem()
        llc1_state_obj = LLC1Search()
        last_created_charge_obj = LastCreatedCharge()

        with main.app.test_request_context():
            user = User()
            user.id = 'id'
            user.first_name = 'joe'
            user.surname = 'bloggs'
            user.organisation = 'testorg'
            user.roles = ['testrole']
            user.status = 'Active'
            user.email = 'username'

            state = LocalLandChargeItem()

            state.statutory_provision = "test_provision"
            state.charge_geographic_description = "test_geo_location"
            state.expiry_date = date(2011, 1, 1)
            state.further_information_location = "test_fi_location"
            state.further_information_reference = "test_fi_reference"

            sess = Session('abc')
            sess.user = user
            sess.add_charge_state = state
            sess.redirect_route = 'some route for redirection'
            sess.two_factor_authentication_passed = True
            sess.two_factor_authentication_code = 123
            sess.two_factor_authentication_redirect_url = 'redirect url'
            sess.two_factor_authentication_generation_time = 'generation time'
            sess.two_factor_authentication_invalid_attempts = 0

            sess.add_lon_charge_state = add_lon_charge_state_obj
            sess.llc1_state = llc1_state_obj
            sess.last_created_charge = last_created_charge_obj
            sess.statutory_provision_list = 'statutory provision list'
            sess.edited_fields = ['field']
            sess.search_extent = search_extent_geo
            sess.filenames = {'form_a': '', 'temporary_lon_cert': '', 'definitive_lon_cert': ''}
            sess.previously_selected_address = {"address": "previously selected address"}
            sess.adding_charge_for_other_authority = False
            sess.submit_token = 'a submit token'
            sess.category_details = category_obj
            sess.category_confirmation = True
            sess.upload_shapefile_processed = True
            sess.charge_added_outside_users_authority = True
            sess.other_authority_update_permission = True
            sess.other_authority_cancel_permission = True

            g.trace_id = "test_id"

            self.assertIsNotNone(sess)

            result = sess.to_dict()

            self.assertEqual(result['add_charge_state']['statutory-provision'], "test_provision")
            self.assertEqual(result['add_charge_state']['charge-geographic-description'], "test_geo_location")
            self.assertEqual(result['add_charge_state']['expiry-date'], "2011-01-01")
            self.assertEqual(result['add_charge_state']['further-information-location'], "test_fi_location")
            self.assertEqual(result['add_charge_state']['further-information-reference'], "test_fi_reference")
            self.assertEqual(result['redirect_route'], 'some route for redirection')
            self.assertEqual(result['add_lon_charge_state'], add_lon_charge_state_obj.to_json())
            self.assertEqual(result['llc1_state'], llc1_state_obj.to_json())
            self.assertEqual(result['last_created_charge'], last_created_charge_obj.__dict__)
            self.assertEqual(result['statutory_provision_list'], 'statutory provision list')
            self.assertEqual(result['edited_fields'], ['field'])
            self.assertEqual(result['search_extent'], search_extent_geo)
            self.assertEqual(result['filenames'], {'form_a': '', 'temporary_lon_cert': '', 'definitive_lon_cert': ''})
            self.assertEqual(result['previously_selected_address'], {"address": "previously selected address"})
            self.assertEqual(result['submit_token'], 'a submit token')
            self.assertEqual(result['category_details'], category_obj.to_json())
            self.assertEqual(result['category_confirmation'], True)
            self.assertEqual(result['upload_shapefile_processed'], True)
            self.assertEqual(result['charge_added_outside_users_authority'], True)
            self.assertEqual(result['other_authority_update_permission'], True)
            self.assertEqual(result['other_authority_cancel_permission'], True)

            two_factor_authentication_result = sess.two_factor_authentication_to_dict()

            self.assertEqual(two_factor_authentication_result['two_factor_authentication_passed'], True)
            self.assertEqual(two_factor_authentication_result['two_factor_authentication_code'], 123)
            self.assertEqual(
                two_factor_authentication_result['two_factor_authentication_redirect_url'],
                'redirect url'
            )
            self.assertEqual(
                two_factor_authentication_result['two_factor_authentication_generation_time'],
                'generation time'
            )
            self.assertEqual(
                two_factor_authentication_result['two_factor_authentication_invalid_attempts'],
                0
            )

    @patch('maintain_frontend.dependencies.session_api.session.SessionAPIService')
    def test_session_invalid(self, mock_session_api):
        with main.app.test_request_context():
            sess = Session('abc')
            mock_session_api.session_valid.return_value = False

            g.trace_id = "test_id"

            self.assertFalse(sess.valid())

    @patch('maintain_frontend.dependencies.session_api.session.SessionAPIService')
    def test_session_invalid_if_cant_get_user(self, mock_session_api):
        with main.app.test_request_context():
            sess = Session('abc')
            mock_session_api.session_valid.return_value = True
            mock_session_api.get_session_state.return_value = None

            g.trace_id = "test_id"

            self.assertFalse(sess.valid())

    @patch('maintain_frontend.dependencies.session_api.session.SessionAPIService')
    def test_session_invalid_if_exception_getting_user(self, mock_session_api):
        with main.app.test_request_context():
            g.trace_id = '123'
            sess = Session('abc')
            mock_session_api.session_valid.return_value = True
            mock_session_api.get_session_state.side_effect = Exception('test')

            self.assertFalse(sess.valid())

    @patch('maintain_frontend.dependencies.session_api.session.SessionAPIService')
    def test_session_valid(self, mock_session_api):
        with main.app.test_request_context():
            sess = Session('abc')

            user = dict()
            user["id"] = "id"
            user["first_name"] = "joe"
            user["surname"] = "bloggs"
            user["email"] = "testemail"
            user["organisation"] = "testorg"
            user["roles"] = ["testrole"]
            user["status"] = "Active"
            user["jwt"] = "MOCK.JWT"

            add_charge_state = dict()
            add_charge_state["statutory-provision"] = "test_provision"
            add_charge_state["charge-address"] = {
                "line-1": "1 The Line",
                "postcode": "AA1 1AA"
            }
            add_charge_state["expiry-date"] = "2011-01-01"
            add_charge_state["further-information-location"] = "test_fi_location"
            add_charge_state["further-information-reference"] = "test_fi_reference"

            lon_charge_state = dict()
            lon_charge_state["applicant_name"] = "applicant_name"
            lon_charge_state["applicant_address"] = {"line-1": "street",
                                                     "line-2": "town",
                                                     "line-3": "county",
                                                     "postcode": "postcode", "country": "country"}
            lon_charge_state["servient_land_interest_description"] = "servient_land_interest_description"
            lon_charge_state["structure_position_and_dimension"] = {
                "height": "Unlimited height",
                "extent-covered": "All of the extent"
            }
            lon_charge_state["documents_filed"] = {"form-a": "form a link", "colour-plan": "colour plan link",
                                                   "temporary-lon-certificate": "temporary cert link",
                                                   "definitive-lon-certificate": "definitive cert link"}
            lon_charge_state["tribunal_definitive_certificate_date"] = "2011-01-01"

            lcc = dict()
            lcc["charge_id"] = 1
            lcc["entry_number"] = 2
            lcc["registration_date"] = "abc"

            state = dict()
            state["add_charge_state"] = add_charge_state
            state["last_created_charge"] = lcc
            state["add_lon_charge_state"] = lon_charge_state
            state["two_factor_authentication_passed"] = True
            state["two_factor_authentication_code"] = 123
            state["two_factor_authentication_redirect_url"] = 'redirect url'
            state["two_factor_authentication_generation_time"] = 'generation time'
            state["two_factor_authentication_invalid_attempts"] = 0

            g.trace_id = "test_id"

            mock_session_api.session_valid.return_value = True
            mock_session_api. \
                get_session_state. \
                side_effect = [user, state, state]

            self.assertTrue(sess.valid())

            self.assertEqual(sess.add_charge_state.statutory_provision, "test_provision")
            self.assertEqual(sess.add_charge_state.expiry_date, date(2011, 1, 1))
            self.assertEqual(sess.add_charge_state.further_information_location, "test_fi_location")
            self.assertEqual(sess.add_charge_state.further_information_reference, "test_fi_reference")
            self.assertEqual(sess.two_factor_authentication_passed, True)
            self.assertEqual(sess.two_factor_authentication_code, 123)
            self.assertEqual(sess.two_factor_authentication_redirect_url, 'redirect url')
            self.assertEqual(sess.two_factor_authentication_generation_time, 'generation time')
            self.assertEqual(sess.two_factor_authentication_invalid_attempts, 0)

    @patch('maintain_frontend.dependencies.session_api.session.SessionAPIService')
    def test_session_commit(self, mock_session_api):
        with main.app.test_request_context():
            user = User()
            user.id = 'id'
            user.email = 'email'
            user.first_name = 'joe'
            user.surname = 'bloggs'
            user.organisation = 'testorg'
            user.roles = ['testrole']
            user.status = 'Active'

            lcc = LastCreatedCharge()

            lcc.charge_id = 1
            lcc.entry_number = 2
            lcc.registration_date = "abc"

            sess = Session('abc')
            sess.user = user
            sess.last_created_charge = lcc

            g.trace_id = "test_id"

            sess.commit()

            mock_session_api.update_session_data. \
                assert_called_with(sess.session_key,
                                   sess.to_dict(),
                                   Session.session_state_key)

    @patch('maintain_frontend.dependencies.session_api.session.SessionAPIService')
    def test_session_commit_2fa_state(self, mock_session_api):
        sess = Session('abc')
        sess.two_factor_authentication_passed = True
        sess.two_factor_authentication_code = 123
        sess.two_factor_authentication_redirect_url = 'redirect url'
        sess.two_factor_authentication_generation_time = 'generation time'
        sess.two_factor_authentication_invalid_attempts = 0

        sess.commit_2fa_state()

        mock_session_api.update_session_data. \
            assert_called_with(sess.session_key,
                               sess.two_factor_authentication_to_dict(),
                               Session.session_2fa_state_key)

    @patch('maintain_frontend.dependencies.session_api.session.SessionAPIService')
    def test_session_geoserver(self, mock_session_api):
        with main.app.test_request_context():
            sess = Session('abc')
            g.trace_id = "test_id"
            token = sess.generate_geoserver()
            mock_session_api.update_session_data.assert_called()
            self.assertIsNotNone(token)
            self.assertIsNotNone(sess.geoserver)
            self.assertIsNotNone(sess.geoserver.token)
            self.assertIsNotNone(sess.geoserver.token_expiry)
