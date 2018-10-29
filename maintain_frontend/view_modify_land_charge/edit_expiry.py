from flask import g, render_template, request, redirect, url_for, current_app
import datetime
from maintain_frontend.services.charge_id_services import calc_display_id
from maintain_frontend.add_land_charge.validation.expiry_validator import ExpiryValidator
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions


def register_routes(bp):
    bp.add_url_rule('/does-charge-expire', view_func=get_expiry, methods=['GET'])
    bp.add_url_rule('/does-charge-expire', view_func=post_expiry, methods=['POST'])


@requires_permission([Permissions.vary_llc])
def get_expiry():
    current_app.logger.info("Endpoint called")
    if g.session.add_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)
    current_app.logger.info("Extracting expiry information from session charge")
    expires = g.session.add_charge_state.expiry_date is not None
    request_body = {
        "does_charge_expire": "yes" if expires else "no",
        "charge_expiry_day": "",
        "charge_expiry_month": "",
        "charge_expiry_year": ""
    }
    if g.session.add_charge_state.expiry_date is not None:
        request_body['charge_expiry_day'] = g.session.add_charge_state.expiry_date.day
        request_body['charge_expiry_month'] = g.session.add_charge_state.expiry_date.month
        request_body['charge_expiry_year'] = g.session.add_charge_state.expiry_date.year

    current_app.logger.info("Expiry information extracted - Rendering response")

    return render_template('expiry.html',
                           request_body=request_body,
                           submit_url=url_for('modify_land_charge.post_expiry')
                           )


@requires_permission([Permissions.vary_llc])
def post_expiry():
    current_app.logger.info("Endpoint called")
    if g.session.add_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)
    does_charge_expire = request.form.get('does_charge_expire', '')
    charge_expiry_day = request.form.get('charge_expiry_day', '')
    charge_expiry_month = request.form.get('charge_expiry_month', '')
    charge_expiry_year = request.form.get('charge_expiry_year', '')

    current_app.logger.info("Validating expiry information")
    validation_errors = ExpiryValidator.validate(
        does_charge_expire,
        charge_expiry_day,
        charge_expiry_month,
        charge_expiry_year
    )

    if validation_errors.errors:
        current_app.logger.warning("Validation errors present - Rendering page with validation errors")
        return render_template(
            'expiry.html',
            validation_errors=validation_errors.errors,
            validation_summary_heading=validation_errors.summary_heading_text,
            request_body=request.form,
            submit_url=url_for('modify_land_charge.post_expiry')
        ), 400

    current_app.logger.info("Field values validated - Updating session charge")
    charge_expiry_date = None
    edited = False
    if does_charge_expire == 'yes':
        if charge_expiry_day and charge_expiry_month and charge_expiry_year:
            charge_expiry_date = datetime.date(
                int(charge_expiry_year),
                int(charge_expiry_month),
                int(charge_expiry_day)
            )
        if g.session.add_charge_state.expiry_date is None \
                or g.session.add_charge_state.expiry_date != charge_expiry_date:
            edited = True
        g.session.add_charge_state.expiry_date = charge_expiry_date
    else:
        if g.session.add_charge_state.expiry_date is not None:
            edited = True
        g.session.add_charge_state.expiry_date = None
    if edited:
        g.session.edited_fields.append('expiry_date')
        g.session.commit()
    charge_disp_id = calc_display_id(g.session.add_charge_state.local_land_charge)
    current_app.logger.info(
        "Session charge updated - Redirecting back to modify_land_charge with local_land_charge='{}'"
        .format(charge_disp_id)
    )
    return redirect(url_for("modify_land_charge.modify_land_charge", local_land_charge=charge_disp_id))
