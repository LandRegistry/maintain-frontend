from flask import url_for
import re

from maintain_frontend.dependencies.search_api.address_service import AddressesService
from maintain_frontend.dependencies.search_api.search_type import SearchType
from maintain_frontend.exceptions import ApplicationError

POSTCODE_REGEX = '^[A-Z]{1,2}[0-9][A-Z0-9]? [0-9][ABD-HJLNP-UW-Z]{2}$'
CHARGE_NUMBER_PREFIX_REGEX = '^(llc|LLC)(-)?\S*$'


class SearchByText(object):
    def __init__(self, logger):
        self.logger = logger

    def process(self, search_query, config, address_api_version="v1"):
        error_response = self.validate_request(search_query)
        if error_response is not None:
            return error_response

        addresses_service = AddressesService(config, address_api_version=address_api_version)

        search_query = search_query.strip().replace("'", "").upper()

        search_for_charge_id = False

        if self.search_valid(search_query, POSTCODE_REGEX):
            self.logger.info("Valid postcode provided: %s", search_query)
            response = addresses_service.get_by(SearchType.POSTCODE.value, search_query)
        elif self.search_valid(search_query, CHARGE_NUMBER_PREFIX_REGEX) is False:
            self.logger.info("Free text provided: %s", search_query)
            response = addresses_service.get_by(SearchType.TEXT.value, search_query)
        else:
            self.logger.info("Invalid search query provided: %s", search_query)
            response_data = {
                "search_message": "Invalid search, please try again",
                "status": "error"
            }

            return response_data

        if address_api_version == "v1":
            return self.process_search_response(response, search_for_charge_id)
        else:
            return self.process_search_response_v2(response)

    def search_valid(self, search_query, regex):
        search_term_valid = re.match(regex, search_query)

        return search_term_valid is not None

    def process_search_response(self, response, search_for_charge_id):
        if response.status_code == 200:
            self.logger.info("Search results found")
            coordinates_array = self.get_all_coordinates(response.json())
            first_result = response.json()[0]

            response_data = {
                "coordinates": coordinates_array,
                "type": first_result['geometry']['type'],
                "status": "success"
            }

            if search_for_charge_id and first_result:
                response_data["charge_url"] = url_for(
                    'view_land_charge.view_land_charge',
                    local_land_charge=first_result["display_id"],
                    _external=True
                )

            return response_data
        elif response.status_code == 404:
            self.logger.info("Valid search format but no results found")
            response_data = {
                "search_message": "Enter a valid postcode or location",
                "status": "error"
            }

            return response_data
        else:
            self.logger.error("Error returned from a get_by function")
            raise ApplicationError(500)

    def process_search_response_v2(self, response):
        if response.status_code == 200:
            self.logger.info("Search results found")

            response_data = {
                "data": response.json(),
                "status": "success"
            }

            return response_data
        elif response.status_code == 404:
            self.logger.info("Valid search format but no results found")
            response_data = {
                "search_message": "Enter a valid postcode or location",
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
                "search_message": "Enter a postcode or location",
                "status": "error"
            }

            return response_data

    def get_all_coordinates(self, response_json):
        array_to_return = []

        for address in response_json:
            current_coordinates_array = []
            if address['geometry']['type'] == "Polygon":
                current_coordinates_array = address['geometry']['coordinates'][0]
            elif address['geometry']['type'] == "LineString":
                current_coordinates_array = address['geometry']['coordinates']
            elif address['geometry']['type'] == "Point":
                current_coordinates_array = [address['geometry']['coordinates']]
            # Recursively handle features/featurecollections - not that nice
            elif address['geometry']['type'] == "FeatureCollection":
                for feature in address['geometry']['features']:
                    current_coordinates_array = current_coordinates_array + self.get_all_coordinates(
                        [{"geometry": feature}])
            elif address['geometry']['type'] == "Feature":
                current_coordinates_array = self.get_all_coordinates([{"geometry": address['geometry']['geometry']}])
            array_to_return.extend(current_coordinates_array)

        return array_to_return
