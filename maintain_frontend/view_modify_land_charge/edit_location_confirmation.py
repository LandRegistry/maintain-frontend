from flask import g, redirect, url_for, render_template, current_app, request
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.decorators import requires_permission
from maintain_frontend.add_land_charge.validation.location_confirmation_validator import LocationConfirmationValidator
from maintain_frontend.services.charge_id_services import calc_display_id
from maintain_frontend.exceptions import ApplicationError


def register_routes(bp):
    bp.add_url_rule('/location-confirmation',
                    view_func=get_location_confirmation,
                    methods=['GET'])
    bp.add_url_rule('/location-confirmation',
                    view_func=post_location_confirmation,
                    methods=['POST'])


@requires_permission([Permissions.vary_llc])
def get_location_confirmation():
    current_app.logger.info('Endpoint called')

    if g.session.add_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)

    if g.session.add_charge_state.geometry is None:
        current_app.logger.error("Geometry not found in session - Returning error")
        raise ApplicationError(500)

    current_app.logger.info("Displaying page 'edit_location_confirmation.html'")

    return render_template('edit_location_confirmation.html',
                           submit_url=url_for('modify_land_charge.post_location_confirmation'))


@requires_permission([Permissions.vary_llc])
def post_location_confirmation():
    current_app.logger.info('Endpoint called')

    if g.session.add_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)

    if g.session.add_charge_state.geometry is None:
        current_app.logger.error("Geometry not found in session - Returning error")
        raise ApplicationError(500)

    confirmation = request.form.get('location-confirmation')

    current_app.logger.info('Running validation')
    validation_errors = LocationConfirmationValidator.validate(confirmation, 'vary')

    if validation_errors.errors:
        current_app.logger.warning('Validation errors occurred')
        return render_template(
            'edit_location_confirmation.html',
            validation_errors=validation_errors.errors,
            validation_summary_heading=validation_errors.summary_heading_text,
            submit_url=url_for('modify_land_charge.post_location_confirmation')
        ), 400

    g.session.charge_added_outside_users_authority = True
    g.session.commit()

    charge_display_id = calc_display_id(g.session.add_charge_state.local_land_charge)
    current_app.logger.info(
        "Session charge updated - Redirecting back to modify_land_charge with local_land_charge='{}'"
        .format(charge_display_id)
    )
    return redirect(url_for("modify_land_charge.modify_land_charge", local_land_charge=charge_display_id))
