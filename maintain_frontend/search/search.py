from flask import render_template, current_app, g, request, jsonify

from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.decorators import requires_permission
from maintain_frontend.services.search_by_text import SearchByText
from maintain_frontend.services.search_by_usrn import SearchByUSRN
from maintain_frontend.services.search_by_area import SearchByArea
from maintain_frontend.services.search_by_postcode import SearchByPostcode
from maintain_frontend.exceptions import ApplicationError


def register_routes(bp):
    bp.add_url_rule('/search', view_func=index, methods=['GET'])
    bp.add_url_rule('/_search/postcode', view_func=search_by_postcode, methods=['GET'])
    bp.add_url_rule('/_search/text/<version>', view_func=search_by_text_endpoint, methods=['GET'])
    bp.add_url_rule('/_search/usrn', view_func=search_by_usrn_endpoint, methods=['GET'])
    bp.add_url_rule('/_search/local_land_charges', view_func=search_by_area_endpoint, methods=['POST'])


@requires_permission([Permissions.browse_llc])
def index():
    # clear the charge data from the session when the search page is loaded, so that any session data regarding
    # varied charges is removed
    current_app.logger.info("Search page requested")
    g.session.add_charge_state = None
    g.session.commit()

    return render_template('search.html', permissions=Permissions.get_user_permissions(g.session.user.permissions),
                           search_extent=g.session.search_extent)


# AJAX Address Search
def search_by_postcode():
    current_app.logger.info("Search by postcode requested")

    if not request.is_xhr:
        current_app.logger.error("Search request not xhr")
        raise ApplicationError(500)

    postcode = request.args.get('postcode')

    search_by_postcode_processor = SearchByPostcode(current_app.logger)
    response = search_by_postcode_processor.process(postcode, current_app.config)

    return jsonify(response)


# AJAX Text Search
def search_by_text_endpoint(version):
    search_term = request.args.get('search_term')
    current_app.logger.info("Search by text requested: {}".format(search_term))

    if not request.is_xhr:
        current_app.logger.error("Search request not xhr")
        raise ApplicationError(500)

    search_by_text_processor = SearchByText(current_app.logger)
    response = search_by_text_processor.process(search_term, current_app.config, address_api_version=version)

    return jsonify(response)


# AJAX USRN Search
def search_by_usrn_endpoint():
    search_term = request.args.get('search_term')
    current_app.logger.info("Search by USRN requested: {}".format(search_term))

    if not request.is_xhr:
        current_app.logger.error("Search request not xhr")
        raise ApplicationError(500)

    search_by_usrn_processor = SearchByUSRN(current_app.logger)
    response = search_by_usrn_processor.process(search_term, current_app.config)

    return jsonify(response)


# AJAX Local Land Charge Search
def search_by_area_endpoint():
    current_app.logger.info("Search by Land Charge requested")

    g.session.search_extent = None
    g.session.commit()

    if not request.is_xhr:
        current_app.logger.error("Search request not xhr")
        raise ApplicationError(500)

    bounding_box = request.get_data().decode()

    search_by_area_processor = SearchByArea(current_app.logger, current_app.config)
    response = search_by_area_processor.process(bounding_box)

    if response['status'] == 200:
        g.session.search_extent = SearchByArea.build_bounding_box_json(bounding_box)
        g.session.commit()

    return jsonify(response)
