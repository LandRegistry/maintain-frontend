from flask import render_template, redirect, url_for, request, current_app, g
from maintain_frontend.services.charge_id_services import calc_display_id
from maintain_frontend.services.field_utilities import has_value_changed
from maintain_frontend.add_land_charge.validation.additional_info_validator import AddChargeAdditionalInfoValidator
from maintain_frontend.add_land_charge.additional_info import get_source_information_list
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions


def register_routes(bp):
    bp.add_url_rule('/source-information', view_func=get_additional_info, methods=['GET'])
    bp.add_url_rule('/source-information', view_func=post_additional_info, methods=['POST'])


@requires_permission([Permissions.vary_llc])
def get_additional_info():
    current_app.logger.info("Endpoint called")
    if g.session.add_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)

    current_app.logger.info("Rendering response")
    return render_template('additional_info.html',
                           information=g.session.add_charge_state.further_information_location,
                           reference=g.session.add_charge_state.further_information_reference,
                           source_information_list=get_source_information_list(),
                           submit_url=url_for('modify_land_charge.post_additional_info'))


@requires_permission([Permissions.vary_llc])
def post_additional_info():
    current_app.logger.info("Endpoint called")
    if g.session.add_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)

    information = request.form['additional-info'].strip()
    reference = request.form['reference'].strip()

    current_app.logger.info("Validating information and reference")
    validation_errors = AddChargeAdditionalInfoValidator.validate(information, reference)

    if validation_errors.errors:
        current_app.logger.warning("Validation errors present - Rendering page with validation errors")
        return render_template('additional_info.html',
                               validation_errors=validation_errors.errors,
                               validation_summary_heading=validation_errors.summary_heading_text,
                               information=information,
                               reference=reference,
                               source_information_list=get_source_information_list(),
                               submit_url=url_for('modify_land_charge.post_additional_info')), 400

    current_app.logger.info("Field values validated - Updating session charge")
    edited = False
    if has_value_changed(g.session.add_charge_state.further_information_location, information):
        g.session.add_charge_state.further_information_location = information
        edited = True

    if has_value_changed(g.session.add_charge_state.further_information_reference, reference):
        g.session.add_charge_state.further_information_reference = reference
        edited = True

    if edited:
        g.session.edited_fields.append('further_information')
        g.session.commit()

    charge_disp_id = calc_display_id(g.session.add_charge_state.local_land_charge)
    current_app.logger.info(
        "Session charge updated - Redirecting back to modify_land_charge with local_land_charge='{}'"
        .format(charge_disp_id)
    )
    return redirect(url_for("modify_land_charge.modify_land_charge", local_land_charge=charge_disp_id))
