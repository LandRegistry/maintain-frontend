from maintain_frontend.dependencies.session_api.user import User
from maintain_frontend.dependencies.session_api.geoserver import Geoserver
from maintain_frontend.dependencies.session_api.session_service import SessionAPIService
from maintain_frontend.dependencies.session_api.last_created_charge import LastCreatedCharge
from maintain_frontend.models import LocalLandChargeItem, LLC1Search, LightObstructionNoticeItem, Category, \
    PaymentLink, PaymentInfo, SearchDetails
from maintain_frontend import config
from flask import current_app
import uuid
import time


class Session(object):
    """Domain object for session."""
    session_user_key = 'user'
    session_state_key = 'maintain_frontend'
    session_2fa_state_key = 'two_factor_authentication'
    session_geoserver_key = 'geoserver'
    session_cookie_name = 'AccessToken'

    def __init__(self, session_key):
        """Initialize session object"""
        self.user = None
        self.session_key = session_key
        self.add_charge_state = None
        self.add_lon_charge_state = None
        self.llc1_state = None
        self.last_created_charge = None
        self.statutory_provision_list = None
        self.edited_fields = None
        self.geoserver = None
        self.redirect_route = None
        self.search_extent = None
        self.filenames = None
        self.previously_selected_address = None
        self.adding_charge_for_other_authority = None
        self.submit_token = None
        self.category_details = None
        self.category_confirmation = None
        self.upload_shapefile_processed = None
        self.charge_added_outside_users_authority = None
        self.other_authority_update_permission = None
        self.other_authority_cancel_permission = None
        self.source_information = None
        self.source_information_id = None
        self.two_factor_authentication_passed = None
        self.two_factor_authentication_code = None
        self.two_factor_authentication_redirect_url = None
        self.two_factor_authentication_generation_time = None
        self.two_factor_authentication_invalid_attempts = None
        self.send_payment_link_info = None
        self.payment_info = None
        self.search_details = None

    def valid(self):
        """Validates the session and populates the data if valid.


        :return: boolean value representing if the session is valid.
        """
        current_app.logger.info("Endpoint called")
        if not SessionAPIService.session_valid(self.session_key):
            current_app.logger.warning("Invalid session key: %s", self.session_key)
            return False
        try:
            if self.user is None:
                current_app.logger.info("Nothing in self.user so populate from session api service")
                self.populate_user()

            # if session does not contain the current logged in user then we can not audit user actions so session is
            # invalid
            if self.user is None:
                current_app.logger.info("Nothing in self.user and no user data in session")
                return False

            if self.add_charge_state is None:
                current_app.logger.info("Nothing in self.add_charge_state so run self.populate_state")
                self.populate_state()

            if self.add_lon_charge_state is None:
                current_app.logger.info("Nothing in self.add_lon_charge_state so run self.populate_state")
                self.populate_state()

            if self.two_factor_authentication_passed is None:
                current_app.logger.info("self.two_factor_authentication_passed is None so run self.populate_2fa_state")
                self.populate_2fa_state()

        except Exception as ex:
            current_app.logger.error(
                'Exception validating session - {}'.format(ex))
            self.expire()
            return False
        return True

    def populate_state(self):
        """Populates the add charge from session state."""
        current_app.logger.info("Method called, getting session state from session api")
        response = SessionAPIService.get_session_state(
            self.session_key, Session.session_state_key)
        if response is not None:
            current_app.logger.info("Non-empty session state contents")
            if 'add_charge_state' in response:
                current_app.logger.info("add_charge_state in session state")
                self.add_charge_state = LocalLandChargeItem.from_json(
                    response['add_charge_state'])
            if 'add_lon_charge_state' in response:
                current_app.logger.info("add_lon_charge_state in session state")
                self.add_lon_charge_state = LightObstructionNoticeItem.from_json(
                    response['add_lon_charge_state'])
            if 'last_created_charge' in response:
                current_app.logger.info("last_created_charge in session state")
                self.last_created_charge = LastCreatedCharge.from_dict(
                    response['last_created_charge'])
            if 'statutory_provision_list' in response:
                current_app.logger.info("statutory_provision_list in session state")
                self.statutory_provision_list = response['statutory_provision_list']
            if 'edited_fields' in response:
                current_app.logger.info("edited_fields in session state")
                self.edited_fields = response['edited_fields']
            if 'llc1_state' in response:
                current_app.logger.info("llc1_state in session state")
                self.llc1_state = LLC1Search.from_json(
                    response['llc1_state']
                )
            if 'redirect_route' in response:
                current_app.logger.info('redirect_route in session state')
                self.redirect_route = response['redirect_route']
            if 'search_extent' in response:
                current_app.logger.info('search_extent in session state')
                self.search_extent = response['search_extent']
            if 'filenames' in response:
                current_app.logger.info('filenames in session state')
                self.filenames = response['filenames']
            if 'previously_selected_address' in response:
                current_app.logger.info('previously_selected_address in session state')
                self.previously_selected_address = response['previously_selected_address']
            if 'adding_charge_for_other_authority' in response:
                current_app.logger.info('adding_charge_for_other_authority in session state')
                self.adding_charge_for_other_authority = response['adding_charge_for_other_authority']
            if 'submit_token' in response:
                current_app.logger.info('submit token in session state')
                self.submit_token = response['submit_token']
            if 'upload_shapefile_processed' in response:
                current_app.logger.info('upload_shapefile_processed in session state')
                self.upload_shapefile_processed = response['upload_shapefile_processed']
            if 'category_details' in response:
                self.category_details = Category.from_dict(response['category_details'])
            if 'category_confirmation' in response:
                self.category_confirmation = response['category_confirmation']
            if 'charge_added_outside_users_authority' in response:
                self.charge_added_outside_users_authority = response['charge_added_outside_users_authority']
            if 'other_authority_update_permission' in response:
                self.other_authority_update_permission = response['other_authority_update_permission']
            if 'other_authority_cancel_permission' in response:
                self.other_authority_cancel_permission = response['other_authority_cancel_permission']
            if 'source_information' in response:
                self.source_information = response['source_information']
            if 'source_information_id' in response:
                self.source_information_id = response['source_information_id']
            if 'send_payment_link_info' in response:
                current_app.logger.info("send_payment_link_info in session state")
                self.send_payment_link_info = PaymentLink.from_json(
                    response['send_payment_link_info']
                )
            if 'payment_info' in response:
                current_app.logger.info("payment_info in session state")
                self.payment_info = PaymentInfo.from_json(
                    response['payment_info']
                )
            if 'search_details' in response:
                self.search_details = SearchDetails.from_json(
                    response['search_details']
                )

    def populate_2fa_state(self):
        response = SessionAPIService.get_session_state(
            self.session_key, Session.session_2fa_state_key)
        if response is not None:
            if 'two_factor_authentication_passed' in response:
                self.two_factor_authentication_passed = response['two_factor_authentication_passed']
            else:
                self.two_factor_authentication_passed = False
            if 'two_factor_authentication_code' in response:
                self.two_factor_authentication_code = response['two_factor_authentication_code']
            if 'two_factor_authentication_redirect_url' in response:
                self.two_factor_authentication_redirect_url = response['two_factor_authentication_redirect_url']
            if 'two_factor_authentication_generation_time' in response:
                self.two_factor_authentication_generation_time = response['two_factor_authentication_generation_time']
            if 'two_factor_authentication_invalid_attempts' in response:
                self.two_factor_authentication_invalid_attempts = \
                    response['two_factor_authentication_invalid_attempts']

    def populate_user(self):
        """Populates the current authenticated user from session state."""
        current_app.logger.info("Method called, getting session user from session api")
        response = SessionAPIService.get_session_state(
            self.session_key, Session.session_user_key)
        if response is not None:
            current_app.logger.info("User data returned from session state")
            self.user = User.from_dict(response)

    def generate_geoserver(self):
        """Generates geoserver token and stores in session, returns token for convenience"""
        current_app.logger.info("Method called, creating geoserver info")
        new_geoserver = Geoserver()
        new_geoserver.token = str(uuid.uuid4())
        new_geoserver.token_expiry = int(time.time()) + config.GEOSERVER_TIMEOUT
        current_app.logger.info("Committing geoserver info to session store")
        SessionAPIService.update_session_data(
            self.session_key, new_geoserver.to_dict(), Session.session_geoserver_key)
        self.geoserver = new_geoserver
        return self.geoserver.token

    def to_dict(self):
        """Builds the valid sections of the session object into a dictionary which can be posted to the session api.


        :return: Dictionary representation of session.
        """
        current_app.logger.info("Method called")
        state = dict()
        if self.add_charge_state is not None:
            state['add_charge_state'] = self.add_charge_state.to_json()
        if self.add_lon_charge_state is not None:
            state['add_lon_charge_state'] = self.add_lon_charge_state.to_json()
        if self.last_created_charge is not None:
            state['last_created_charge'] = self.last_created_charge.__dict__
        if self.statutory_provision_list is not None:
            state['statutory_provision_list'] = self.statutory_provision_list
        if self.edited_fields is not None:
            state['edited_fields'] = self.edited_fields
        if self.llc1_state is not None:
            state['llc1_state'] = self.llc1_state.to_json()
        if self.redirect_route is not None:
            state['redirect_route'] = self.redirect_route
        if self.search_extent is not None:
            state['search_extent'] = self.search_extent
        if self.filenames is not None:
            state['filenames'] = self.filenames
        if self.previously_selected_address is not None:
            state['previously_selected_address'] = self.previously_selected_address
        if self.adding_charge_for_other_authority is not None:
            state['adding_charge_for_other_authority'] = self.adding_charge_for_other_authority
        if self.submit_token is not None:
            state['submit_token'] = self.submit_token
        if self.upload_shapefile_processed is not None:
            state['upload_shapefile_processed'] = self.upload_shapefile_processed
        if self.category_details is not None:
            state['category_details'] = self.category_details.to_json()
        if self.category_confirmation is not None:
            state['category_confirmation'] = self.category_confirmation
        if self.charge_added_outside_users_authority is not None:
            state['charge_added_outside_users_authority'] = self.charge_added_outside_users_authority
        if self.other_authority_update_permission is not None:
            state['other_authority_update_permission'] = self.other_authority_update_permission
        if self.other_authority_cancel_permission is not None:
            state['other_authority_cancel_permission'] = self.other_authority_cancel_permission
        if self.source_information is not None:
            state['source_information'] = self.source_information
        if self.source_information_id is not None:
            state['source_information_id'] = self.source_information_id
        if self.send_payment_link_info is not None:
            state['send_payment_link_info'] = self.send_payment_link_info.to_json()
        if self.payment_info is not None:
            state['payment_info'] = self.payment_info.to_json()
        if self.search_details is not None:
            state['search_details'] = self.search_details.to_json()

        return state

    def two_factor_authentication_to_dict(self):
        state = dict()
        if self.two_factor_authentication_passed is not None:
            state['two_factor_authentication_passed'] = self.two_factor_authentication_passed
        if self.two_factor_authentication_code is not None:
            state['two_factor_authentication_code'] = self.two_factor_authentication_code
        if self.two_factor_authentication_redirect_url is not None:
            state['two_factor_authentication_redirect_url'] = self.two_factor_authentication_redirect_url
        if self.two_factor_authentication_generation_time is not None:
            state['two_factor_authentication_generation_time'] = self.two_factor_authentication_generation_time
        if self.two_factor_authentication_invalid_attempts is not None:
            state['two_factor_authentication_invalid_attempts'] = self.two_factor_authentication_invalid_attempts
        return state

    def commit(self):
        """Saves the current session representation to the session store."""
        current_app.logger.info("Method called")
        SessionAPIService.update_session_data(
            self.session_key, self.to_dict(), Session.session_state_key)

    def commit_2fa_state(self):
        SessionAPIService.update_session_data(
            self.session_key, self.two_factor_authentication_to_dict(), Session.session_2fa_state_key)

    def expire(self):
        """Expires the current session token."""
        current_app.logger.info("Method called")
        SessionAPIService.expire_session(self.session_key)
