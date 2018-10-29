from flask import render_template, redirect, url_for, request, g, current_app
from maintain_frontend.services.charge_id_services import calc_display_id
from maintain_frontend.services.field_utilities import has_value_changed
from maintain_frontend.add_land_charge.validation.financial_charge_details_validator \
    import FinancialChargeDetailsValidator
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.services.number_converter import NumberConverter

NO_INTEREST_IS_PAYABLE = 'No interest is payable'


def register_routes(bp):
    bp.add_url_rule('/amount-and-interest', view_func=get_financial_charge, methods=['GET'])
    bp.add_url_rule('/amount-and-interest', view_func=post_financial_charge, methods=['POST'])


@requires_permission([Permissions.vary_llc])
def get_financial_charge():
    current_app.logger.info("Endpoint called")
    if g.session.add_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)

    interest_paid_indicator = "No"
    interest_rate = None

    if g.session.add_charge_state.rate_of_interest:
        if g.session.add_charge_state.rate_of_interest == NO_INTEREST_IS_PAYABLE:
            interest_paid_indicator = "No"
            interest_rate = None
        else:
            interest_paid_indicator = "Yes"
            interest_rate = g.session.add_charge_state.rate_of_interest

    request_body = {
        'amount-secured': g.session.add_charge_state.amount_originally_secured,
        'interest-paid-indicator': interest_paid_indicator,
        'interest-rate': interest_rate
    }

    current_app.logger.info("Rendering template")
    return render_template('financial_charge_details.html',
                           submit_url=url_for('modify_land_charge.post_financial_charge'),
                           request_body=request_body)


@requires_permission([Permissions.vary_llc])
def post_financial_charge():
    current_app.logger.info("Endpoint called")
    if g.session.add_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)

    amount_secured = NumberConverter.format_number_string(request.form.get('amount-secured', ''), leading_char='£',
                                                          force_two_dp=True)
    interest_paid_indicator = request.form.get('interest-paid-indicator', '')
    interest_rate = request.form.get('interest-rate', '')

    current_app.logger.info("Running validation")
    validation_errors = FinancialChargeDetailsValidator.validate(amount_secured, interest_paid_indicator,
                                                                 interest_rate)
    if validation_errors.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template(
            'financial_charge_details.html',
            validation_errors=validation_errors.errors,
            validation_summary_heading=validation_errors.summary_heading_text,
            request_body=request.form,
            submit_url=url_for('modify_land_charge.post_financial_charge')
        ), 400

    if interest_paid_indicator == "No":
        interest_rate = NO_INTEREST_IS_PAYABLE
        current_app.logger.info("Updating session object with charge amount: '%s' and no interest rate",
                                amount_secured)

    edited = False
    if has_value_changed(g.session.add_charge_state.amount_originally_secured, amount_secured):
        g.session.add_charge_state.amount_originally_secured = amount_secured
        g.session.edited_fields.append('amount_originally_secured')
        edited = True

    if has_value_changed(g.session.add_charge_state.rate_of_interest, interest_rate):
        g.session.add_charge_state.rate_of_interest = interest_rate
        g.session.edited_fields.append('rate_of_interest')
        edited = True

    if edited:
        g.session.commit()

    charge_display_id = calc_display_id(g.session.add_charge_state.local_land_charge)
    current_app.logger.info(
        "Session charge updated - Redirecting back to modify_land_charge with local_land_charge='{}'"
        .format(charge_display_id)
    )
    return redirect(url_for("modify_land_charge.modify_land_charge", local_land_charge=charge_display_id))
