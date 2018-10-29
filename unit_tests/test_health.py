from maintain_frontend.main import app
import unittest
from unit_tests.utilities import Utilities


class TestHealth(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        Utilities.mock_session_cookie_unittest(self)

    def test_health(self):
        self.assertEqual((self.app.get('/health')).status_code, 200)
