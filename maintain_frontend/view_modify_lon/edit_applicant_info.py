from flask import render_template, redirect, url_for, request, g, current_app
from maintain_frontend.services.charge_id_services import calc_display_id
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.decorators import requires_permission
from maintain_frontend.dependencies.country_register.country_register_service import get_sorted_countries
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.add_lon.validation.applicant_info_validator import ApplicantInfoValidator
from maintain_frontend.services.address_converter import AddressConverter


def register_routes(bp):
    bp.add_url_rule('/who-is-applying', view_func=edit_applicant_info_get, methods=['GET'])
    bp.add_url_rule('/who-is-applying', view_func=edit_applicant_info_post, methods=['POST'])


@requires_permission([Permissions.vary_lon])
def edit_applicant_info_get():
    if g.session.add_lon_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)

    applicant_address = g.session.add_lon_charge_state.applicant_address

    request_body = {
        'applicant_name': g.session.add_lon_charge_state.applicant_name or ''
    }

    if g.session.add_lon_charge_state.applicant_address:
        if 'line-1' in applicant_address:
            request_body['address_line_1'] = applicant_address['line-1']
        if 'line-2' in applicant_address:
            request_body['address_line_2'] = applicant_address['line-2']
        if 'line-3' in applicant_address:
            request_body['address_line_3'] = applicant_address['line-3']
        if 'line-4' in applicant_address:
            request_body['address_line_4'] = applicant_address['line-4']
        if 'line-5' in applicant_address:
            request_body['address_line_5'] = applicant_address['line-5']
        if 'line-6' in applicant_address:
            request_body['address_line_6'] = applicant_address['line-6']
        if 'country' in applicant_address:
            request_body['country'] = applicant_address['country']
        if 'postcode' in applicant_address:
            request_body['postcode'] = applicant_address['postcode']

    current_app.logger.info("Rendering template")
    return render_template('applicant_info.html', submit_url=url_for('modify_lon.edit_applicant_info_post'),
                           country_list=get_sorted_countries(),
                           request_body=request_body)


@requires_permission([Permissions.vary_lon])
def edit_applicant_info_post():
    if g.session.add_lon_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)

    address_form = request.form

    current_app.logger.info("Running validation")
    validation_error_builder = ApplicantInfoValidator.validate(address_form)

    if validation_error_builder.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template('applicant_info.html',
                               validation_errors=validation_error_builder.errors,
                               validation_summary_heading=validation_error_builder.summary_heading_text,
                               submit_url=url_for('modify_lon.edit_applicant_info_post'),
                               country_list=get_sorted_countries(),
                               request_body=request.form), 400

    applicant_address = AddressConverter.condense_address(address_form)
    applicant_name = address_form.get('applicant_name')

    current_app.logger.info("Updating session object")

    if applicant_name != g.session.add_lon_charge_state.applicant_name:
        g.session.add_lon_charge_state.applicant_name = applicant_name
        g.session.edited_fields['applicant-name'] = 'Name'

    if applicant_address != g.session.add_lon_charge_state.applicant_address:
        g.session.add_lon_charge_state.applicant_address = applicant_address
        g.session.edited_fields['applicant-address'] = 'Address'

    g.session.commit()

    charge_display_id = calc_display_id(g.session.add_lon_charge_state.local_land_charge)

    current_app.logger.info(
        "Session charge updated - Redirecting back to modify_lon with charge_id='{}'".format(charge_display_id)
    )

    return redirect(url_for("modify_lon.modify_lon_details_get", charge_id=charge_display_id))
