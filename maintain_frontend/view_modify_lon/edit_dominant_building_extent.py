from flask import render_template, redirect, url_for, request, g, current_app
from maintain_frontend.services.charge_id_services import calc_display_id
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.add_land_charge.validation.location_validator import AddLocationMapValidator
import json


def register_routes(bp):
    bp.add_url_rule('/dominant-building-extent', view_func=edit_dominant_building_extent_get, methods=['GET'])
    bp.add_url_rule('/dominant-building-extent', view_func=edit_dominant_building_extent_post, methods=['POST'])


@requires_permission([Permissions.vary_lon])
def edit_dominant_building_extent_get():
    if g.session.add_lon_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)

    return render_template('dominant_building_extent.html',
                           submit_url=url_for('modify_lon.edit_dominant_building_extent_post'),
                           information=g.session.add_lon_charge_state.geometry)


@requires_permission([Permissions.vary_lon])
def edit_dominant_building_extent_post():
    if g.session.add_lon_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)

    information = None
    postcode_to_zoom = ''
    if g.session.add_lon_charge_state.charge_address:
        postcode_to_zoom = g.session.add_lon_charge_state.charge_address['postcode']

    if 'saved-features' in request.form:
        information = json.loads(request.form['saved-features'].strip())

    validation_errors = AddLocationMapValidator.validate(information, "Draw the extent", "Draw the extent")

    if validation_errors.errors:
        current_app.logger.warning("Validation errors present - Rendering page with validation errors")
        return render_template(
            'dominant_building_extent.html',
            validation_errors=validation_errors.errors,
            validation_summary_heading=validation_errors.summary_heading_text,
            information=information,
            postcode=postcode_to_zoom,
            submit_url=url_for('modify_lon.edit_dominant_building_extent_post')
        ), 400

    if g.session.add_lon_charge_state.geometry != information:
        g.session.edited_fields['geometry'] = 'Extent'
        g.session.add_lon_charge_state.geometry = information
        g.session.commit()

    charge_display_id = calc_display_id(g.session.add_lon_charge_state.local_land_charge)
    current_app.logger.info(
        "Session charge updated - Redirecting back to modify_land_charge with local_land_charge='{}'".format(
            charge_display_id
        )
    )

    return redirect(url_for("modify_lon.modify_lon_details_get", charge_id=charge_display_id))
