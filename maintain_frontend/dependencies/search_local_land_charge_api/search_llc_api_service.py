from flask import g
from maintain_frontend import config


class SearchLLCAPIService(object):

    @staticmethod
    def get_by_reference_number(reference_number):
        return g.requests.get("{}/paid-searches/{}".format(
            config.SEARCH_LOCAL_LAND_CHARGE_API_URL,
            reference_number))
