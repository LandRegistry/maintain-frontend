import json
from flask import g, redirect, url_for, render_template, request, current_app
from maintain_frontend.add_land_charge.validation.location_validator import AddLocationMapValidator
from maintain_frontend.services.charge_id_services import calc_display_id
from maintain_frontend.services.field_utilities import has_value_changed
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.dependencies.local_authority_api.local_authority_api_service import LocalAuthorityService
from maintain_frontend.services.build_extents_from_features import build_extents_from_features


def register_routes(bp):
    bp.add_url_rule('/update-extent', view_func=get_location, methods=['GET'])
    bp.add_url_rule('/update-extent', view_func=post_location, methods=['POST'])


@requires_permission([Permissions.vary_llc])
def get_location():
    current_app.logger.info("Endpoint called")
    if g.session.add_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)

    g.session.charge_added_outside_users_authority = False
    g.session.commit()

    if g.session.add_charge_state.geometry is not None:
        current_app.logger.info("Rendering template with session charge geometry")
        return render_template('location.html',
                               information=g.session.add_charge_state.geometry,
                               submit_url=url_for('modify_land_charge.post_location'))

    current_app.logger.info("Rendering template with no geometry")
    return render_template('location.html',
                           submit_url=url_for('modify_land_charge.post_location'))


@requires_permission([Permissions.vary_llc])
def post_location():
    current_app.logger.info("Endpoint called")
    if g.session.add_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)
    information = None

    if 'saved-features' in request.form:
        information = json.loads(request.form['saved-features'].strip())

    current_app.logger.info("Validating location geometry")
    validation_errors = AddLocationMapValidator.validate(information)

    if validation_errors.errors:
        current_app.logger.warning("Validation errors present - Rendering page with validation errors")
        return render_template(
            'location.html',
            validation_errors=validation_errors.errors,
            validation_summary_heading=validation_errors.summary_heading_text,
            information=information,
            submit_url=url_for('modify_land_charge.post_location')
        ), 400

    current_app.logger.info("Field values validated - Updating session charge")
    if has_value_changed(g.session.add_charge_state.geometry, information):
        g.session.edited_fields.append('location_info')
        g.session.add_charge_state.geometry = information
        g.session.commit()

    if 'LLC LR Admins' not in g.session.user.roles and 'LLC LR Users' not in g.session.user.roles:
        result = LocalAuthorityService(current_app.config).get_authorities_by_extent(
            build_extents_from_features(information))
        if len(result) != 1 or g.session.user.organisation not in result:
            return redirect(url_for('modify_land_charge.get_location_confirmation'))

    charge_display_id = calc_display_id(g.session.add_charge_state.local_land_charge)
    current_app.logger.info(
        "Session charge updated - Redirecting back to modify_land_charge with local_land_charge='{}'"
        .format(charge_display_id)
    )
    return redirect(url_for("modify_land_charge.modify_land_charge", local_land_charge=charge_display_id))
