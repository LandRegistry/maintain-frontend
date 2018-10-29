from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from flask import render_template, g, url_for, current_app, redirect, request
from maintain_frontend.llc1.validation.search_extent_validator import SearchExtentValidator
from maintain_frontend.dependencies.local_authority_api.local_authority_api_service import LocalAuthorityService
import json


def register_routes(bp):
    bp.add_url_rule('/create-official-search/draw-search-extent', view_func=llc1_get_extent, methods=['GET'])
    bp.add_url_rule('/create-official-search/draw-search-extent-no-location',
                    view_func=llc1_get_extent_no_location, methods=['GET'])
    bp.add_url_rule('/create-official-search/draw-search-extent', view_func=llc1_set_extent, methods=['POST'])


@requires_permission([Permissions.request_llc1])
def llc1_get_extent():
    current_app.logger.info('Endpoint called')
    if g.session.llc1_state is None:
        current_app.logger.info('Redirecting to: %s', url_for("create_llc1.create_llc1"))
        return redirect(url_for("create_llc1.create_llc1"))

    current_app.logger.info("Render template 'search_extent.html'")
    return render_template("search_extent.html",
                           information=g.session.llc1_state.extent,
                           coordinates=g.session.llc1_state.map_coordinates,
                           submit_url=url_for('create_llc1.llc1_set_extent'))


@requires_permission([Permissions.request_llc1])
def llc1_get_extent_no_location():
    current_app.logger.info('Endpoint called')
    if g.session.llc1_state is None:
        current_app.logger.info('Redirecting to: %s', url_for("create_llc1.create_llc1"))
        return redirect(url_for("create_llc1.create_llc1"))

    g.session.llc1_state.map_coordinates = None
    g.session.commit()
    current_app.logger.info("Redirecting to %s", url_for("create_llc1.llc1_get_extent"))
    return redirect(url_for("create_llc1.llc1_get_extent"))


@requires_permission([Permissions.request_llc1])
def llc1_set_extent():
    current_app.logger.info('Endpoint called')
    if g.session.llc1_state is None:
        current_app.logger.info('Redirect to %s', url_for('create_llc1.create_llc1'))
        return redirect(url_for('create_llc1.create_llc1'))

    search_extent = None
    if 'saved-features' in request.form:
        search_extent = json.loads(request.form['saved-features'].strip())

    current_app.logger.info("Running validation")
    validation_errors = SearchExtentValidator.validate(search_extent)

    if validation_errors.errors:
        current_app.logger.warning('Validation errors occurred')
        return render_template("search_extent.html",
                               coordinates=g.session.llc1_state.map_coordinates,
                               submit_url=url_for('create_llc1.llc1_set_extent'),
                               validation_errors=validation_errors.errors,
                               validation_summary_heading=validation_errors.summary_heading_text), 400

    current_app.logger.info("Updating session object")
    g.session.llc1_state.extent = search_extent
    g.session.commit()

    local_authority_service = LocalAuthorityService(current_app.config)
    formatted_search_extent = build_extents_from_features(search_extent)
    is_extent_within_migrated_area = local_authority_service.is_extent_within_migrated_area(formatted_search_extent)

    if not is_extent_within_migrated_area:
        current_app.logger.warning('Drawn extent is outside of migrated area')
        return render_template("search_extent.html",
                               information=search_extent,
                               submit_url=url_for('create_llc1.llc1_set_extent'),
                               is_valid_search_extent=is_extent_within_migrated_area), 400

    current_app.logger.info("Redirecting to next step: %s", url_for("create_llc1.llc1_get_description"))
    return redirect(url_for("create_llc1.llc1_get_description"))


def build_extents_from_features(feature_collection):
    geometries = []
    for feature in feature_collection['features']:
        geometries.append(feature['geometry'])

    result = {
        "type": "geometrycollection",
        "geometries": geometries
    }
    return json.dumps(result)
