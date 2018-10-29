from flask import render_template, redirect, url_for, request, g, current_app
from maintain_frontend.add_land_charge.validation.land_compensation_type_validator import LandCompensationTypeValidator
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions


def register_routes(bp):
    bp.add_url_rule('/add-local-land-charge/is-advance-payment-known',
                    view_func=get_land_compensation_type, methods=['GET'])
    bp.add_url_rule('/add-local-land-charge/is-advance-payment-known',
                    view_func=post_land_compensation_type, methods=['POST'])


@requires_permission([Permissions.add_llc])
def get_land_compensation_type():
    if g.session.add_charge_state is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_land_charge.new"))
        return redirect(url_for("add_land_charge.new"))

    current_app.logger.info("Displaying page 'charge_type.html'")
    return render_template('land_compensation_type.html',
                           submit_url=url_for('add_land_charge.post_land_compensation_type'))


@requires_permission([Permissions.add_llc])
def post_land_compensation_type():
    current_app.logger.info("Endpoint called with advance-payment-known = '%s'",
                            request.form['advance-payment-known'] if 'advance-payment-known' in request.form else None)
    if g.session.add_charge_state is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_land_charge.new"))
        return redirect(url_for("add_land_charge.new"))

    advance_payment_known = request.form.get('advance-payment-known', '')

    current_app.logger.info("Running validation")
    validation_errors = LandCompensationTypeValidator.validate(advance_payment_known)
    if validation_errors.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template(
            'land_compensation_type.html',
            validation_errors=validation_errors.errors,
            validation_summary_heading=validation_errors.summary_heading_text,
            submit_url=url_for('add_land_charge.post_land_compensation_type')
        ), 400

    if advance_payment_known == "Yes":
        # S52 route
        g.session.add_charge_state.statutory_provision = 'Land Compensation Act 1973 section 52(8)'
        # Clear any values entered for amount and interest rate
        g.session.add_charge_state.land_sold_description = None
        g.session.add_charge_state.land_works_particulars = None
        # Remove fields from edited fields list as the fields will not display on review page
        if 'land_sold_description' in g.session.edited_fields:
            g.session.edited_fields.remove('land_sold_description')
        if 'land_works_particulars' in g.session.edited_fields:
            g.session.edited_fields.remove('land_works_particulars')
        g.session.commit()
        next_url = url_for("add_land_charge.get_land_compensation_payment")
    else:
        # S8 route
        g.session.add_charge_state.statutory_provision = 'Land Compensation Act 1973 section 8(4)'
        # Clear any values entered for amount and interest rate
        g.session.add_charge_state.land_compensation_paid = None
        g.session.add_charge_state.amount_of_compensation = None
        g.session.add_charge_state.land_compensation_amount_type = None
        g.session.add_charge_state.land_capacity_description = None
        # Remove fields from edited fields list as the fields will not display on review page
        if 'land_compensation_paid' in g.session.edited_fields:
            g.session.edited_fields.remove('land_compensation_paid')
        if 'amount_of_compensation' in g.session.edited_fields:
            g.session.edited_fields.remove('amount_of_compensation')
        if 'land_compensation_amount_type' in g.session.edited_fields:
            g.session.edited_fields.remove('land_compensation_amount_type')
        if 'land_capacity_description' in g.session.edited_fields:
            g.session.edited_fields.remove('land_capacity_description')
        g.session.commit()
        next_url = url_for("add_land_charge.get_land_compensation_land_sold")

    current_app.logger.info("Redirecting to next step: %s", next_url)
    return redirect(next_url)
