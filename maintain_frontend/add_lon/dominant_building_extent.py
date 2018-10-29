from flask import g, render_template, redirect, url_for, current_app, request
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.add_land_charge.validation.location_validator import AddLocationMapValidator
from maintain_frontend.add_lon.routing.review_router import ReviewRouter
import json


def register_routes(bp):
    bp.add_url_rule('/add-light-obstruction-notice/dominant-building-extent',
                    view_func=get_dominant_building_extent, methods=['GET'])
    bp.add_url_rule('/add-light-obstruction-notice/dominant-building-extent',
                    view_func=post_dominant_building_extent, methods=['POST'])


@requires_permission([Permissions.add_lon])
def get_dominant_building_extent():
    if g.session.add_lon_charge_state is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_lon.new"))
        return redirect(url_for("add_lon.new"))

    current_app.logger.info("Displaying page 'dominant_building_extent.html'")

    postcode_to_zoom = ''
    if g.session.add_lon_charge_state.charge_address:
        postcode_to_zoom = g.session.add_lon_charge_state.charge_address['postcode']

    return render_template('dominant_building_extent.html',
                           submit_url=url_for("add_lon.post_dominant_building_extent"),
                           postcode=postcode_to_zoom,
                           information=g.session.add_lon_charge_state.geometry)


@requires_permission([Permissions.add_lon])
def post_dominant_building_extent():
    if g.session.add_lon_charge_state is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_lon.new"))
        return redirect(url_for("add_lon.new"))

    information = None

    if 'saved-features' in request.form:
        information = json.loads(request.form['saved-features'].strip())

    current_app.logger.info("Running validation")
    validation_errors = AddLocationMapValidator.validate(information, "Draw the extent", "Draw the extent")

    if validation_errors.errors:
        current_app.logger.warning("Validation errors occurred")

        postcode_to_zoom = ''
        if g.session.add_lon_charge_state.charge_address:
            postcode_to_zoom = g.session.add_lon_charge_state.charge_address['postcode']

        return render_template(
            'dominant_building_extent.html',
            validation_errors=validation_errors.errors,
            validation_summary_heading=validation_errors.summary_heading_text,
            submit_url=url_for("add_lon.post_dominant_building_extent"),
            information=information,
            postcode=postcode_to_zoom
        ), 400

    current_app.logger.info("Updating session object")
    ReviewRouter.update_edited_field('geometry', information)

    g.session.add_lon_charge_state.geometry = information
    g.session.commit()

    return redirect(ReviewRouter.get_redirect_url("add_lon.get_land_interest"))
