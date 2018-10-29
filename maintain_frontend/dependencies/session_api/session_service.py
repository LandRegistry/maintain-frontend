from maintain_frontend.config import SESSION_API_URL
from maintain_frontend.exceptions import ApplicationError
from flask import current_app, g


class SessionAPIService(object):
    @staticmethod
    def get_session_state(token_id, subsection):
        """Returns either a JSON object containing the session contents, or returns None if the session isn't found.


        :param token_id:  Identifier for the session.
        :param subsection: The subsection of session state that should be retrieved.
        :return: Returns dictionary representation of the response or None.
        """
        current_app.logger.info("Method called")
        try:
            response = g.requests.get(
                '{}/{}/state/{}'.format(SESSION_API_URL, token_id, subsection,
                                        headers={'X-Trace-ID': g.trace_id})
            )
        except Exception as ex:
            current_app.logger.warning(
                'Failed to get session state. TraceID : {} - Exception - {}'.format(g.trace_id, ex))
            return None

        json = response.json()

        if response.status_code != 200:
            if response.status_code != 404:
                current_app.logger.warning(
                    'Failed to get session state - TraceID : {} - Status: {}, Message: {}'.format(
                        g.trace_id,
                        response.status_code,
                        response.text))
            return None

        return json

    @staticmethod
    def create_session(username):
        """Creates a new session variable and returns the session Id.


        :param username: username used to create the session token.
        :return: Session key as string.
        :exception Raises application exception in the event of a non successful http response code or issue making
        request.
        """
        current_app.logger.info("Method called")
        try:
            response = g.requests.post(SESSION_API_URL, data=username, headers={'X-Trace-ID': g.trace_id})
        except Exception as ex:
            current_app.logger.exception(
                'Failed to create session. TraceID : {} - Exception - {}'.format(g.trace_id, ex))
            raise ApplicationError(500)

        if response.status_code != 201 and response.status_code != 200:
            current_app.logger.exception('Failed to create session. TraceID : {} - Status code:{}, message:{}'.format(
                g.trace_id,
                response.status_code,
                response.text)
            )
            raise ApplicationError(500)
        return response.text

    @staticmethod
    def update_session_data(token_id, data, subsection):
        """Updates the contents of an existing session variable.


        :param token_id:  Identifier for the session.
        :param data: The data to be stored in the session state.
        :param subsection: The section of the session state that the data should be stored.
        :exception Raises application exception in the event of a non successful http response code or issue making
        request.
        """
        current_app.logger.info("Method called")
        try:
            response = g.requests.put(
                '{}/{}/state/{}'.format(SESSION_API_URL, token_id, subsection),
                json=data, headers={'X-Trace-ID': g.trace_id}
            )
        except Exception as ex:
            current_app.logger.exception(
                'Failed to update session. TraceID : {} - Exception - {}'.format(g.trace_id, ex))
            raise ApplicationError(500)

        if response.status_code != 201 and response.status_code != 204:
            error_message = 'Error when updating session data ' \
                            'for session ID {}. TraceID : {} - Message - {}'.format(token_id,
                                                                                    g.trace_id,
                                                                                    response.text)
            current_app.logger.exception(error_message)
            raise ApplicationError(500)

    @staticmethod
    def session_valid(session_key):
        """Validates the session token against the session api.


        :param session_key: Identifier for the session.
        :return: Boolean value representing if the session if valid.
        """
        current_app.logger.info("Method called")
        try:
            response = g.requests.get('{}/{}'.format(
                SESSION_API_URL, session_key), headers={'X-Trace-ID': g.trace_id})
            if response.status_code != 200:
                return False
            return True
        except Exception as ex:
            current_app.logger.warning('Failed to get session - {}. TraceID : {}'.format(ex, g.trace_id))
            return False

    @staticmethod
    def expire_session(session_key):
        """Tells the session api to expire the token.


        :param session_key: Identifier for the session.
        """
        current_app.logger.info("Method called")
        try:
            g.requests.delete('{}/{}'.format(SESSION_API_URL, session_key), headers={'X-Trace-ID': g.trace_id})
        except Exception as ex:
            current_app.logger.error(
                'Failed to expire session - {}. TraceID : {}'.format(ex, g.trace_id))
