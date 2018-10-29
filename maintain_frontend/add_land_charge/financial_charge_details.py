from flask import render_template, redirect, url_for, request, g, current_app
from maintain_frontend.add_land_charge.validation.financial_charge_details_validator \
    import FinancialChargeDetailsValidator
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.add_land_charge.routing.review_router import ReviewRouter
from maintain_frontend.services.number_converter import NumberConverter

NO_INTEREST_IS_PAYABLE = 'No interest is payable'


def register_routes(bp):
    bp.add_url_rule('/add-local-land-charge/amount-and-interest',
                    view_func=get_financial_charge_details, methods=['GET'])
    bp.add_url_rule('/add-local-land-charge/amount-and-interest',
                    view_func=post_financial_charge_details, methods=['POST'])


@requires_permission([Permissions.add_llc])
def get_financial_charge_details():
    if g.session.add_charge_state is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_land_charge.new"))
        return redirect(url_for("add_land_charge.new"))

    interest_paid_indicator = None
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

    current_app.logger.info("Displaying page 'financial_charge_details.html'")
    return render_template('financial_charge_details.html',
                           request_body=request_body,
                           submit_url=url_for('add_land_charge.post_financial_charge_details'))


@requires_permission([Permissions.add_llc])
def post_financial_charge_details():
    current_app.logger.info("Endpoint called with amount-secured = '%s', interest-paid-indicator = '%s', "
                            "interest-rate = '%s' and ",
                            request.form.get('amount-secured', ''), request.form.get('interest-paid-indicator', ''),
                            request.form.get('interest-rate', ''))
    if g.session.add_charge_state is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_land_charge.new"))
        return redirect(url_for("add_land_charge.new"))

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
            submit_url=url_for('add_land_charge.post_financial_charge_details')
        ), 400

    if interest_paid_indicator == "No":
        interest_rate = NO_INTEREST_IS_PAYABLE
        current_app.logger.info("Updating session object with charge amount: '%s' and no interest rate",
                                amount_secured)

    ReviewRouter.update_edited_field('amount_originally_secured', amount_secured)
    ReviewRouter.update_edited_field('rate_of_interest', interest_rate)

    g.session.add_charge_state.amount_originally_secured = amount_secured
    g.session.add_charge_state.rate_of_interest = interest_rate
    g.session.commit()

    current_app.logger.info("Redirecting to next step: %s",
                            ReviewRouter.get_redirect_url("add_land_charge.get_charge_date"))
    return redirect(ReviewRouter.get_redirect_url("add_land_charge.get_charge_date"))
