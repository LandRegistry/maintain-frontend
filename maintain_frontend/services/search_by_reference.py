import re
from maintain_frontend.dependencies.search_api.local_land_charge_service import LocalLandChargeService
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.services.charge_id_services import CHARGE_NUMBER_REGEX


class SearchByReference(object):
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def process(self, search_query):
        local_land_charge_service = LocalLandChargeService(self.config)

        if self.search_valid(search_query, CHARGE_NUMBER_REGEX):
            self.logger.info("Searching by charge ID: %s", search_query)
            response = local_land_charge_service.get_by_charge_number(search_query)
        else:
            self.logger.info("Searching by reference number: %s", search_query)
            response = local_land_charge_service.get_by_reference_number(search_query)

        return self.process_search_response(response)

    def search_valid(self, search_query, regex):
        search_term_valid = re.match(regex, search_query)
        return search_term_valid is not None

    def process_search_response(self, response):
        if response.status_code == 200:
            self.logger.info("Search results found")
            return {
                "status_code": response.status_code,
                "results": response.json()
            }
        elif response.status_code == 404:
            self.logger.info("No results found")
            return {
                "status_code": response.status_code,
                "results": None
            }
        else:
            raise ApplicationError(500)
