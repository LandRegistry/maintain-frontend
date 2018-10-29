from flask import render_template, redirect, url_for, request, g, current_app
from maintain_frontend.add_land_charge.validation.financial_charge_validator \
    import FinancialChargeValidator
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.add_land_charge.routing.review_router import ReviewRouter


def register_routes(bp):
    bp.add_url_rule('/add-local-land-charge/amount-originally-secured',
                    view_func=get_financial_charge, methods=['GET'])
    bp.add_url_rule('/add-local-land-charge/amount-originally-secured',
                    view_func=post_financial_charge, methods=['POST'])


@requires_permission([Permissions.add_llc])
def get_financial_charge():
    if g.session.add_charge_state is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_land_charge.new"))
        return redirect(url_for("add_land_charge.new"))

    current_app.logger.info("Displaying page 'financial_charge.html'")
    return render_template('financial_charge.html',
                           submit_url=url_for('add_land_charge.post_financial_charge'))


@requires_permission([Permissions.add_llc])
def post_financial_charge():
    current_app.logger.info("Endpoint called with amount-known-indicator = '%s'",
                            request.form.get('amount-known-indicator', ''))
    if g.session.add_charge_state is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_land_charge.new"))
        return redirect(url_for("add_land_charge.new"))

    amount_known_indicator = request.form.get('amount-known-indicator', '')

    current_app.logger.info("Running validation")
    validation_errors = FinancialChargeValidator.validate(amount_known_indicator)
    if validation_errors.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template(
            'financial_charge.html',
            validation_errors=validation_errors.errors,
            validation_summary_heading=validation_errors.summary_heading_text,
            request_body=request.form,
            submit_url=url_for('add_land_charge.post_financial_charge')
        ), 400

    if amount_known_indicator == "Yes":
        next_url = url_for("add_land_charge.get_financial_charge_details")
    else:
        # Clear any values entered for amount and interest rate
        g.session.add_charge_state.amount_originally_secured = None
        g.session.add_charge_state.rate_of_interest = None
        g.session.commit()
        # Remove fields from edited fields list as the fields will not display on review page
        if 'amount_originally_secured' in g.session.edited_fields:
            g.session.edited_fields.remove('amount_originally_secured')
        if 'rate_of_interest' in g.session.edited_fields:
            g.session.edited_fields.remove('rate_of_interest')
        next_url = ReviewRouter.get_redirect_url("add_land_charge.get_charge_date")
    g.session.commit()

    current_app.logger.info("Redirecting to next step: %s", next_url)
    return redirect(next_url)
