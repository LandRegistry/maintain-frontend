import re

from maintain_frontend.dependencies.search_api.address_service import AddressesService
from maintain_frontend.dependencies.search_api.search_type import SearchType
from maintain_frontend.exceptions import ApplicationError

POSTCODE_REGEX = '^([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z]' \
                 '[A-Ha-hJ-Yj-y][0-9]{1,2})|(([A-Za-z][0-9][A-Za-z])|' \
                 '([A-Za-z][A-Ha-hJ-Yj-y][0-9]?[A-Za-z])))) [0-9][A-Za-z]{2})$'


class SearchByPostcode(object):
    def __init__(self, logger):
        self.logger = logger

    def process(self, search_query, config):
        error_response = self.validate_request(search_query)
        if error_response is not None:
            return error_response

        addresses_service = AddressesService(config)

        search_query = search_query.strip().replace("'", "").upper()

        if self.search_valid(search_query, POSTCODE_REGEX):
            self.logger.info("Valid postcode provided: %s", search_query)
            response = addresses_service.get_by(SearchType.POSTCODE.value, search_query)
        else:
            self.logger.info("Invalid postcode provided: %s", search_query)
            response_data = {
                "search_message": "No match found",
                "inline_message": "Try a different postcode",
                "status": "error"
            }

            return response_data

        return self.process_search_response(response)

    def search_valid(self, search_query, regex):
        search_term_valid = re.match(regex, search_query)

        return search_term_valid is not None

    def process_search_response(self, response):
        if response.status_code == 200:
            self.logger.info("Search results found")

            response_data = {
                "data": response.json(),
                "status": "success"
            }

            return response_data
        elif response.status_code == 400:
            self.logger.info("Invalid search. {0}".format(response.json()))
            response_data = {
                "search_message": "No match found",
                "inline_message": "Try a different postcode",
                "status": "error"
            }

            return response_data
        elif response.status_code == 404:
            self.logger.info("Valid search format but no results found")
            response_data = {
                "search_message": "No match found",
                "inline_message": "Try a different postcode",
                "status": "error"
            }

            return response_data
        else:
            self.logger.error("Error returned from a get_by function")
            raise ApplicationError(500)

    def validate_request(self, search_query):
        if not search_query:
            self.logger.info("No search query provided")
            response_data = {
                "search_message": "Enter a postcode",
                "inline_message": "Search for a different postcode if the address you need is not listed.",
                "status": "error"
            }

            return response_data
