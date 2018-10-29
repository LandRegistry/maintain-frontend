from unittest.mock import patch
from maintain_frontend.dependencies.session_api.session import Session


class Utilities(object):
    """Helper class that mocks out the session for test making app requests.


    Supports both unittest framework and flasktest framework.

    Place in test set up Utilities.mock_session_cookie_unittest(self)

    or

    Utilities.mock_session_cookie_flask_test(self)
    """

    @staticmethod
    def mock_session_cookie_unittest(unittest):
        patcher = patch('maintain_frontend.app.Session')
        unittest.addCleanup(patcher.stop)
        unittest.mock_session = patcher.start()
        unittest.app.set_cookie('localhost', Session.session_cookie_name, 'cookie_value')
        unittest.mock_session.return_value.valid.return_value = True
        unittest.mock_session.session_cookie_name = Session.session_cookie_name

    @staticmethod
    def mock_session_cookie_flask_test(flasktest):
        patcher = patch('maintain_frontend.app.Session')
        flasktest.mock_session = patcher.start()
        flasktest.mock_session.return_value.valid.return_value = True
        flasktest.mock_session.session_cookie_name = Session.session_cookie_name
