from flask import render_template, redirect, url_for, request, g, current_app
from maintain_frontend.services.charge_id_services import calc_display_id
from maintain_frontend.add_land_charge.validation.charge_date_validator import ChargeDateValidator
from datetime import date
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions


def register_routes(bp):
    bp.add_url_rule('/when-was-charge-created', view_func=get_charge_date, methods=['GET'])
    bp.add_url_rule('/when-was-charge-created', view_func=post_charge_date, methods=['POST'])


@requires_permission([Permissions.vary_llc])
def get_charge_date():
    current_app.logger.info("Endpoint called")
    if g.session.add_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)
    create_date = g.session.add_charge_state.charge_creation_date
    if create_date:
        charge_date = {
            'day': str(create_date.day),
            'month': str(create_date.month),
            'year': str(create_date.year)
        }
    else:
        charge_date = None
    current_app.logger.info("Rendering template")
    return render_template('charge_date.html',
                           submit_url=url_for('modify_land_charge.post_charge_date'),
                           date=charge_date)


@requires_permission([Permissions.vary_llc])
def post_charge_date():
    current_app.logger.info("Endpoint called")
    if g.session.add_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)

    day = request.form.get('date-day')
    month = request.form.get('date-month')
    year = request.form.get('date-year')
    current_app.logger.info("Validating charge date")
    validation_errors = ChargeDateValidator.validate(day, month, year)
    if validation_errors.errors:
        current_app.logger.warning("Validation errors present - Rendering page with validation errors")
        charge_date = {
            'day': day,
            'month': month,
            'year': year
        }
        return render_template('charge_date.html',
                               validation_errors=validation_errors.errors,
                               validation_summary_heading=validation_errors.summary_heading_text,
                               submit_url=url_for('modify_land_charge.post_charge_date'),
                               request=request,
                               date=charge_date)

    current_app.logger.info("Field values validated - Updating session charge")
    if year and month and day:
        new_date = date(int(year), int(month), int(day))
    else:
        new_date = None
    if g.session.add_charge_state.charge_creation_date != new_date:
        g.session.add_charge_state.charge_creation_date = new_date
        g.session.edited_fields.append('charge_creation_date')
        g.session.commit()

    charge_display_id = calc_display_id(g.session.add_charge_state.local_land_charge)
    current_app.logger.info(
        "Session charge updated - Redirecting back to modify_land_charge with local_land_charge='{}'"
        .format(charge_display_id)
    )
    return redirect(url_for("modify_land_charge.modify_land_charge", local_land_charge=charge_display_id))
