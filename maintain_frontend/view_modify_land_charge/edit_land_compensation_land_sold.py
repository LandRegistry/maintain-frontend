from flask import render_template, redirect, url_for, request, current_app, g
from maintain_frontend.add_land_charge.validation.land_compensation_land_sold_validator import \
    LandCompensationLandSoldValidator
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.services.charge_id_services import calc_display_id
from maintain_frontend.services.field_utilities import has_value_changed


def register_routes(bp):
    bp.add_url_rule('/land-sold-to-authority', view_func=get_land_compensation_land_sold, methods=['GET'])
    bp.add_url_rule('/land-sold-to-authority', view_func=post_land_compensation_land_sold, methods=['POST'])


@requires_permission([Permissions.vary_llc])
def get_land_compensation_land_sold():
    current_app.logger.info('Endpoint called')
    if g.session.add_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)

    request_body = {
        'land-sold-description': g.session.add_charge_state.land_sold_description,
        'land-works-particulars': g.session.add_charge_state.land_works_particulars
    }

    current_app.logger.info("Displaying page 'land_compensation_land_sold.html'")
    return render_template('land_compensation_land_sold.html',
                           request_body=request_body,
                           submit_url=url_for('modify_land_charge.post_land_compensation_land_sold'))


@requires_permission([Permissions.vary_llc])
def post_land_compensation_land_sold():
    current_app.logger.info("Endpoint called with land-sold-description = '%s' and land-works-particulars = '%s'",
                            request.form.get('land-sold-description', ''),
                            request.form.get('land-works-particulars', ''))

    if g.session.add_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)

    description = request.form['land-sold-description'].strip()
    land_works_particulars = request.form['land-works-particulars'].strip()

    current_app.logger.info('Running validation')
    validation_errors = LandCompensationLandSoldValidator.validate(description, land_works_particulars)

    if validation_errors.errors:
        current_app.logger.warning('Validation errors occurred')
        return render_template('land_compensation_land_sold.html',
                               validation_errors=validation_errors.errors,
                               validation_summary_heading=validation_errors.summary_heading_text,
                               request_body=request.form,
                               submit_url=url_for('modify_land_charge.post_land_compensation_land_sold')), 400

    current_app.logger.info("Updating session object with land-sold-description = '%s' and "
                            "land-works-particulars = '%s'", description, land_works_particulars)

    charge_display_id = calc_display_id(g.session.add_charge_state.local_land_charge)
    edited = False
    if has_value_changed(g.session.add_charge_state.land_sold_description, description):
        edited = True
        g.session.edited_fields.append('land_sold_description')
        g.session.add_charge_state.land_sold_description = description
    if has_value_changed(g.session.add_charge_state.land_works_particulars, land_works_particulars):
        edited = True
        g.session.edited_fields.append('land_works_particulars')
        g.session.add_charge_state.land_works_particulars = land_works_particulars

    if edited:
        g.session.commit()

    current_app.logger.info("Redirecting to next step: %s",
                            url_for("modify_land_charge.modify_land_charge", local_land_charge=charge_display_id))
    return redirect(url_for("modify_land_charge.modify_land_charge", local_land_charge=charge_display_id))
