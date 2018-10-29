from flask import Blueprint, current_app, request, jsonify
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.dependencies.search_api.address_service import AddressesService
import re
from maintain_frontend.dependencies.search_api.search_type import SearchType

# Blueprint Definition
address_finder_bp = Blueprint('address_finder', __name__,
                              static_url_path='/static/address_finder',
                              static_folder='static',
                              template_folder='templates')


@address_finder_bp.route('/address-finder/_search')
def get_addresses():
    current_app.logger.info("Search by address requested")
    if not request.is_xhr:
        current_app.logger.error("Search request not xhr")
        raise ApplicationError(500)

    postcode = request.args.get('search_term')
    addresses_service = AddressesService(current_app.config)

    if not postcode:
        current_app.logger.info("No search query provided")
        validation_errors = {
            "search_postcode_message": "Enter postcode or choose 'Enter address manually'",
            "search_message_inline_message": "Enter postcode or choose 'Enter address manually'",
            "status": "error"
        }

        return jsonify(validation_errors)

    search_query = postcode.strip().replace("'", "").upper()
    postcode_regex_check = '^([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z]' \
                           '[A-Ha-hJ-Yj-y][0-9]{1,2})|(([A-Za-z][0-9][A-Za-z])|' \
                           '([A-Za-z][A-Ha-hJ-Yj-y][0-9]?[A-Za-z])))) [0-9][A-Za-z]{2})$'

    valid_postcode = re.match(postcode_regex_check, search_query)

    if valid_postcode is not None:
        current_app.logger.info("Valid postcode provided: %s", search_query)
        response = addresses_service.get_by(SearchType.POSTCODE.value, search_query)
    else:
        current_app.logger.info("Invalid postcode provided: %s", search_query)
        validation_errors = {
            "search_postcode_message": "Invalid postcode, please try again",
            "status": "error"
        }
        return jsonify(validation_errors)

    if response.status_code == 200:
        current_app.logger.info("Search results found")
        addresses = response.json()
        response_data = {
            "addresses": addresses,
            "status": "success"
        }
        return jsonify(response_data)
    elif response.status_code == 400:
        current_app.logger.info("Invalid postcode provided: %s", search_query)
        validation_errors = {
            "search_postcode_message": "Invalid postcode, please try again",
            "search_message_inline_message": "Invalid postcode, please try again",
            "status": "error"
        }
        return jsonify(validation_errors)
    elif response.status_code == 404:
        current_app.logger.info("Valid search format but no results found")
        validation_errors = {
            "search_postcode_message": "Results not found. Try another search",
            "search_message_inline_message": "Results not found. Try another search",
            "status": "error"
        }
        return jsonify(validation_errors)
    else:
        current_app.logger.error("Error returned from a get_by function")
        raise ApplicationError(500)
