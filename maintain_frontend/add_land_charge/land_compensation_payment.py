from flask import render_template, redirect, url_for, request, g, current_app
from maintain_frontend.add_land_charge.validation.land_compensation_payment_validator \
    import LandCompensationPaymentValidator
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.add_land_charge.routing.review_router import ReviewRouter
from maintain_frontend.services.number_converter import NumberConverter


def register_routes(bp):
    bp.add_url_rule('/add-local-land-charge/advance-payment',
                    view_func=get_land_compensation_payment, methods=['GET'])
    bp.add_url_rule('/add-local-land-charge/advance-payment',
                    view_func=post_land_compensation_payment, methods=['POST'])


@requires_permission([Permissions.add_llc])
def get_land_compensation_payment():
    if g.session.add_charge_state is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_land_charge.new"))
        return redirect(url_for("add_land_charge.new"))

    request_body = {
        'land-compensation-paid': g.session.add_charge_state.land_compensation_paid,
        'land-compensation-amount-type': g.session.add_charge_state.land_compensation_amount_type,
        'amount-of-compensation': g.session.add_charge_state.amount_of_compensation
    }

    current_app.logger.info("Displaying page 'land_compensation_payment.html'")
    return render_template('land_compensation_payment.html',
                           request_body=request_body,
                           submit_url=url_for('add_land_charge.post_land_compensation_payment'))


@requires_permission([Permissions.add_llc])
def post_land_compensation_payment():
    land_compensation_paid = NumberConverter.format_number_string(request.form.get('land-compensation-paid'),
                                                                  leading_char='£', force_two_dp=True)

    amount_of_compensation = NumberConverter.format_number_string(request.form.get('amount-of-compensation'),
                                                                  leading_char='£', force_two_dp=True)
    land_compensation_amount_type = request.form.get('land-compensation-amount-type')

    current_app.logger.info("Endpoint called with land-compensation-paid = '%s', land-compensation-amount-type = '%s'",
                            land_compensation_paid,
                            amount_of_compensation,
                            land_compensation_amount_type)
    if g.session.add_charge_state is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_land_charge.new"))
        return redirect(url_for("add_land_charge.new"))

    current_app.logger.info("Running validation")
    validation_errors = LandCompensationPaymentValidator.validate(land_compensation_paid,
                                                                  amount_of_compensation, False)
    if validation_errors.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template(
            'land_compensation_payment.html',
            validation_errors=validation_errors.errors,
            validation_summary_heading=validation_errors.summary_heading_text,
            request_body=request.form,
            submit_url=url_for('add_land_charge.post_land_compensation_payment')
        ), 400

    current_app.logger.info("Updating session object with land compensation amount: '%s' and \
                            land compensation amount type: '%s'",
                            land_compensation_paid, land_compensation_amount_type)

    ReviewRouter.update_edited_field('land_compensation_paid', land_compensation_paid)
    ReviewRouter.update_edited_field('amount_of_compensation', amount_of_compensation)
    ReviewRouter.update_edited_field('land_compensation_amount_type', land_compensation_amount_type)

    g.session.add_charge_state.land_compensation_paid = land_compensation_paid
    g.session.add_charge_state.amount_of_compensation = amount_of_compensation
    g.session.add_charge_state.land_compensation_amount_type = land_compensation_amount_type
    g.session.commit()

    # Force the flow to go to the next page if that value is not in the session (in case browser back button is used)
    if not g.session.add_charge_state.land_capacity_description:
        next_url = url_for("add_land_charge.get_land_compensation_owned")
    else:
        next_url = ReviewRouter.get_redirect_url("add_land_charge.get_land_compensation_owned")
    current_app.logger.info("Redirecting to next step: %s", next_url)
    return redirect(next_url)
