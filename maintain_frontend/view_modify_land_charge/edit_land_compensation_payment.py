from flask import render_template, redirect, url_for, request, g, current_app
from maintain_frontend.add_land_charge.validation.land_compensation_payment_validator \
    import LandCompensationPaymentValidator
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.decorators import requires_permission
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.services.charge_id_services import calc_display_id
from maintain_frontend.services.field_utilities import has_value_changed
from maintain_frontend.services.number_converter import NumberConverter


def register_routes(bp):
    bp.add_url_rule('/advance-payment', view_func=get_land_compensation_payment, methods=['GET'])
    bp.add_url_rule('/advance-payment', view_func=post_land_compensation_payment, methods=['POST'])


@requires_permission([Permissions.vary_llc])
def get_land_compensation_payment():
    current_app.logger.info("Endpoint called")
    if g.session.add_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)

    request_body = {
        'land-compensation-paid': g.session.add_charge_state.land_compensation_paid,
        'amount-of-compensation': g.session.add_charge_state.amount_of_compensation,
        'land-compensation-amount-type': g.session.add_charge_state.land_compensation_amount_type
    }

    current_app.logger.info("Displaying page 'land_compensation_payment.html'")
    return render_template('land_compensation_payment.html',
                           request_body=request_body,
                           submit_url=url_for('modify_land_charge.post_land_compensation_payment'))


@requires_permission([Permissions.vary_llc])
def post_land_compensation_payment():
    current_app.logger.info("Endpoint called")
    if g.session.add_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)

    land_compensation_paid = NumberConverter.format_number_string(request.form.get('land-compensation-paid'),
                                                                  leading_char='£', force_two_dp=True)

    amount_of_compensation = NumberConverter.format_number_string(request.form.get('amount-of-compensation'),
                                                                  leading_char='£', force_two_dp=True)
    land_compensation_amount_type = request.form.get('land-compensation-amount-type')

    current_app.logger.info("Running validation")
    validation_errors = LandCompensationPaymentValidator.validate(land_compensation_paid, amount_of_compensation, True)
    if validation_errors.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template(
            'land_compensation_payment.html',
            validation_errors=validation_errors.errors,
            validation_summary_heading=validation_errors.summary_heading_text,
            request_body=request.form,
            submit_url=url_for('modify_land_charge.post_land_compensation_payment')
        ), 400

    current_app.logger.info("Updating session object with land compensation amount: '%s' , \
                                    total compensation: '%s' and land compensation amount type: '%s'",
                            land_compensation_paid, amount_of_compensation, land_compensation_amount_type)

    charge_display_id = calc_display_id(g.session.add_charge_state.local_land_charge)
    edited = False
    if has_value_changed(g.session.add_charge_state.land_compensation_paid, land_compensation_paid):
        g.session.edited_fields.append('land_compensation_paid')
        g.session.add_charge_state.land_compensation_paid = land_compensation_paid
        edited = True
    if has_value_changed(g.session.add_charge_state.amount_of_compensation, amount_of_compensation):
        g.session.edited_fields.append('amount_of_compensation')
        g.session.add_charge_state.amount_of_compensation = amount_of_compensation
        edited = True
    if has_value_changed(g.session.add_charge_state.land_compensation_amount_type, land_compensation_amount_type):
        g.session.edited_fields.append('land_compensation_amount_type')
        g.session.add_charge_state.land_compensation_amount_type = land_compensation_amount_type
        edited = True
    if edited:
        g.session.commit()

    current_app.logger.info("Redirecting to next step: %s",
                            url_for("modify_land_charge.modify_land_charge", local_land_charge=charge_display_id))
    return redirect(url_for("modify_land_charge.modify_land_charge", local_land_charge=charge_display_id))
