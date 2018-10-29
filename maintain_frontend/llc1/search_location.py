from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from flask import current_app, g, url_for, redirect, render_template, request
from maintain_frontend.dependencies.search_api.address_service import AddressesService
from maintain_frontend.llc1.validation.location_validator import LocationValidator
from maintain_frontend.dependencies.search_api.search_type import SearchType
import re


def register_routes(bp):
    bp.add_url_rule('/create-official-search/location', view_func=llc1_get_location, methods=['GET'])
    bp.add_url_rule('/create-official-search/location', view_func=llc1_post_location, methods=['POST'])


@requires_permission([Permissions.request_llc1])
def llc1_get_location():
    current_app.logger.info('Endpoint called')
    if g.session.llc1_state is None:
        current_app.logger.info('Redirecting to: %s', url_for("create_llc1.create_llc1"))
        return redirect(url_for("create_llc1.create_llc1"))

    current_app.logger.info("Displaying page 'search_location.html")
    return render_template('search_location.html',
                           submit_url=url_for("create_llc1.llc1_post_location"))


@requires_permission([Permissions.request_llc1])
def llc1_post_location():
    current_app.logger.info('Submit location')
    if g.session.llc1_state is None:
        current_app.logger.info('Redirecting to: %s', url_for("create_llc1.create_llc1"))
        return redirect(url_for("create_llc1.create_llc1"))

    location = request.form['location'].strip()

    current_app.logger.info("Running validation")
    validation_errors = LocationValidator.validate(location)

    if validation_errors.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template('search_location.html',
                               validation_errors=validation_errors.errors,
                               validation_summary_heading=validation_errors.summary_heading_text,
                               data=location,
                               submit_url=url_for("create_llc1.llc1_post_location")), 400

    # TODO(repeat): this repeats some of the search screen stuff
    location_data = search_for_location(location)
    if location_data is None:
        errors = {
            'location': {
                'inline_message': 'Address not found. Try a new address',
                'summary_message': 'No matching address found'
            }
        }
        return render_template('search_location.html',
                               validation_errors=errors,
                               validation_summary_heading='There are errors on this page',
                               data=location,
                               submit_url=url_for("create_llc1.llc1_post_location")), 400

    g.session.llc1_state.map_coordinates = location_data
    g.session.commit()

    current_app.logger.info("Redirecting to " + url_for("create_llc1.llc1_get_extent"))
    return redirect(url_for("create_llc1.llc1_get_extent"))


def search_for_location(location):
    search_query = location.strip().replace("'", "").upper()
    postcode_regex_check = '^([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z]' \
                           '[A-Ha-hJ-Yj-y][0-9]{1,2})|(([A-Za-z][0-9][A-Za-z])|' \
                           '([A-Za-z][A-Ha-hJ-Yj-y][0-9]?[A-Za-z])))) [0-9][A-Za-z]{2})$'
    uprn_regex_check = '^[0-9]{6,12}$'

    # Validation to decipher whether the search term is a postcode, uprn or free text.
    valid_postcode = re.match(postcode_regex_check, search_query)
    valid_uprn = re.match(uprn_regex_check, search_query)

    address_service = AddressesService(current_app.config)
    if valid_postcode is not None:
        search_type = 'postcode'
        current_app.logger.info("Valid postcode provided: %s", search_query)
        response = address_service.get_by(SearchType.POSTCODE.value, search_query)
    elif valid_uprn is not None:
        search_type = 'uprn'
        current_app.logger.info("Valid UPRN provided: %s", search_query)
        response = address_service.get_by(SearchType.UPRN.value, search_query)
    else:
        search_type = 'text'
        current_app.logger.info("Free text provided: %s", search_query)
        response = address_service.get_by(SearchType.TEXT.value, search_query)

    if response.status_code == 404:
        return None

    current_app.logger.info("Search results found")
    geo = response.json()
    coordinates_array = get_all_coordinates(geo)
    return {
        'search_type': search_type,
        'coordinates': coordinates_array,
        'location': location
    }


def get_all_coordinates(response_json):
    current_app.logger.info("Attempting to retrieve co-ordinates")
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
                current_coordinates_array = current_coordinates_array + get_all_coordinates([{"geometry": feature}])
        elif address['geometry']['type'] == "Feature":
            current_coordinates_array = get_all_coordinates([{"geometry": address['geometry']['geometry']}])
        array_to_return.extend(current_coordinates_array)

    return array_to_return
