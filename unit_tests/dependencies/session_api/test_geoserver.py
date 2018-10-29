from maintain_frontend.dependencies.session_api.geoserver import Geoserver
from unittest import TestCase


class TestGeoserverDomain(TestCase):

    def test_geoserver_initialisation(self):
        geo = Geoserver()
        geo.token = 'atoken'
        geo.token_expiry = 1234567

        self.assertIsNotNone(geo)
        self.assertEqual(geo.token, 'atoken')
        self.assertEqual(geo.token_expiry, 1234567)

    def test_geoserver_from_dict(self):
        test = dict()
        test["token"] = "atoken"
        test["token_expiry"] = 1234567
        geo = Geoserver.from_dict(test)

        self.assertIsNotNone(geo)
        self.assertEqual(geo.token, 'atoken')
        self.assertEqual(geo.token_expiry, 1234567)

    def test_geoserver_to_dict(self):
        geo = Geoserver()
        geo.token = 'atoken'
        geo.token_expiry = 1234567
        geo_dict = geo.to_dict()

        self.assertIsNotNone(geo_dict)
        self.assertEqual(geo_dict['token'], 'atoken')
        self.assertEqual(geo_dict['token_expiry'], 1234567)
