from flask import render_template, redirect, url_for, request, g, current_app
from maintain_frontend.services.charge_id_services import calc_display_id
from maintain_frontend.services.field_utilities import has_value_changed
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.add_land_charge.validation.charge_description_validator import ChargeDescriptionValidator


def register_routes(bp):
    bp.add_url_rule('/charge-description', view_func=get_charge_description, methods=['GET'])
    bp.add_url_rule('/charge-description', view_func=post_charge_description, methods=['POST'])


@requires_permission([Permissions.vary_llc])
def get_charge_description():
    current_app.logger.info("Endpoint called")
    if g.session.add_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)
    current_app.logger.info("Rendering template")
    return render_template('charge_description.html',
                           data=g.session.add_charge_state.supplementary_information,
                           submit_url=url_for('modify_land_charge.post_charge_description'))


@requires_permission([Permissions.vary_llc])
def post_charge_description():
    current_app.logger.info("Endpoint called")
    if g.session.add_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)
    description = request.form['charge-description'].strip()

    current_app.logger.info("Validating charge reason")
    validation_errors = ChargeDescriptionValidator.validate(description)

    if validation_errors.errors:
        current_app.logger.warning("Validation errors present - Rendering page with validation errors")
        return render_template('charge_description.html',
                               data=description,
                               validation_errors=validation_errors.errors,
                               validation_summary_heading=validation_errors.summary_heading_text,
                               submit_url=url_for('modify_land_charge.post_charge_description')
                               ), 400
    current_app.logger.info("Field values validated - Updating session charge")
    if has_value_changed(g.session.add_charge_state.supplementary_information, description):
        g.session.add_charge_state.supplementary_information = description
        g.session.edited_fields.append('charge_description')
        g.session.commit()

    charge_display_id = calc_display_id(g.session.add_charge_state.local_land_charge)
    current_app.logger.info(
        "Session charge updated - Redirecting back to modify_land_charge with local_land_charge='{}'".format(
            charge_display_id)
    )
    return redirect(url_for("modify_land_charge.modify_land_charge", local_land_charge=charge_display_id))
