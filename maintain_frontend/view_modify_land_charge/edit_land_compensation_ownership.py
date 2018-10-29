from flask import render_template, redirect, url_for, request, g, current_app
from maintain_frontend.add_land_charge.validation.land_compensation_owned_validator \
    import LandCompensationOwnedValidator
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.decorators import requires_permission
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.services.charge_id_services import calc_display_id
from maintain_frontend.services.field_utilities import has_value_changed


def register_routes(bp):
    bp.add_url_rule('/how-is-land-owned', view_func=get_land_compensation_ownership, methods=['GET'])
    bp.add_url_rule('/how-is-land-owned', view_func=post_land_compensation_ownership, methods=['POST'])


@requires_permission([Permissions.vary_llc])
def get_land_compensation_ownership():
    current_app.logger.info("Endpoint called")
    if g.session.add_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)

    land_ownership_indicator = None
    land_ownership_other = None

    if g.session.add_charge_state.land_capacity_description:
        if g.session.add_charge_state.land_capacity_description not in ['Freehold', 'Leasehold']:
            land_ownership_indicator = "Other"
            land_ownership_other = g.session.add_charge_state.land_capacity_description
        else:
            land_ownership_indicator = g.session.add_charge_state.land_capacity_description
            land_ownership_other = None

    request_body = {
        'land-owned-indicator': land_ownership_indicator,
        'land-owned-other': land_ownership_other
    }

    current_app.logger.info("Displaying page 'land_compensation_owned.html'")
    return render_template('land_compensation_owned.html',
                           request_body=request_body,
                           submit_url=url_for('modify_land_charge.post_land_compensation_ownership'))


@requires_permission([Permissions.vary_llc])
def post_land_compensation_ownership():
    current_app.logger.info("Endpoint called")
    if g.session.add_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)

    land_ownership_indicator = request.form.get('land-owned-indicator', '')
    land_ownership_other = request.form.get('land-owned-other', '')

    current_app.logger.info("Running validation")
    validation_errors = LandCompensationOwnedValidator.validate(land_ownership_indicator, land_ownership_other)
    if validation_errors.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template(
            'land_compensation_owned.html',
            validation_errors=validation_errors.errors,
            validation_summary_heading=validation_errors.summary_heading_text,
            request_body=request.form,
            submit_url=url_for('modify_land_charge.post_land_compensation_ownership')
        ), 400

    edited = False
    if g.session.add_charge_state.land_capacity_description in ['Freehold', 'Leasehold']:
        if land_ownership_indicator == "Other":
            edited = True
            g.session.add_charge_state.land_capacity_description = land_ownership_other
        elif has_value_changed(g.session.add_charge_state.land_capacity_description, land_ownership_indicator):
            edited = True
            g.session.add_charge_state.land_capacity_description = land_ownership_indicator
    elif g.session.add_charge_state.land_capacity_description not in ['Freehold', 'Leasehold']:
        if land_ownership_indicator in ['Freehold', 'Leasehold']:
            edited = True
            g.session.add_charge_state.land_capacity_description = land_ownership_indicator
        elif has_value_changed(g.session.add_charge_state.land_capacity_description, land_ownership_other):
            edited = True
            g.session.add_charge_state.land_capacity_description = land_ownership_other

    if edited:
        g.session.edited_fields.append('land_compensation_ownership')
        g.session.commit()

    current_app.logger.info("Updating session object with land capacity description: '%s'",
                            g.session.add_charge_state.land_capacity_description)

    charge_display_id = calc_display_id(g.session.add_charge_state.local_land_charge)

    current_app.logger.info("Redirecting to next step: %s",
                            url_for("modify_land_charge.modify_land_charge", local_land_charge=charge_display_id))
    return redirect(url_for("modify_land_charge.modify_land_charge", local_land_charge=charge_display_id))
