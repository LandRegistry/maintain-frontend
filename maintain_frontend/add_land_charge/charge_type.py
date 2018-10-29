from flask import render_template, redirect, url_for, request, g, current_app

from maintain_frontend.add_land_charge.validation.charge_type_validator import ChargeTypeValidator
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.decorators import requires_permission
from maintain_frontend.dependencies.maintain_api.categories import CategoryService
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.config import SCHEMA_VERSION


def register_routes(bp):
    bp.add_url_rule('/add-local-land-charge/choose-charge-category',
                    view_func=get_charge_type, methods=['GET'])
    bp.add_url_rule('/add-local-land-charge/choose-charge-category',
                    view_func=post_charge_type, methods=['POST'])


@requires_permission([Permissions.add_llc])
def get_charge_type():
    if g.session.add_charge_state is None:
        current_app.logger.info("Redirecting to: %s",
                                url_for("add_land_charge.new"))
        return redirect(url_for("add_land_charge.new"))

    reset_category_info()

    categories = CategoryService.get_categories()

    current_app.logger.info("Displaying page 'charge_type.html'")
    return render_template('charge_type.html',
                           categories=categories,
                           submit_url=url_for('add_land_charge.post_charge_type'))


@requires_permission([Permissions.add_llc])
def post_charge_type():
    current_app.logger.info("Endpoint called with charge-type = '%s'",
                            request.form['charge-type'] if 'charge-type' in request.form else None)
    if g.session.add_charge_state is None:
        current_app.logger.info("Redirecting to: %s",
                                url_for("add_land_charge.new"))
        return redirect(url_for("add_land_charge.new"))

    charge_type = request.form.get('charge-type')

    current_app.logger.info("Running validation")
    validation_errors = ChargeTypeValidator.validate(charge_type)
    if validation_errors.errors:
        current_app.logger.warning("Validation errors occurred")
        categories = CategoryService.get_categories()
        return render_template(
            'charge_type.html',
            categories=categories,
            validation_errors=validation_errors.errors,
            validation_summary_heading=validation_errors.summary_heading_text,
            submit_url=url_for('add_land_charge.post_charge_type')
        ), 400

    current_app.logger.info(
        "Updating session object with charge type: %s", charge_type)
    if g.session.add_charge_state.charge_type is not None and g.session.add_charge_state.charge_type != charge_type:
        current_app.logger.info("Clearing session - charge type changed")
        if g.session.adding_charge_for_other_authority:
            authority = g.session.add_charge_state.originating_authority
        else:
            authority = g.session.user.organisation
        g.session.add_charge_state = LocalLandChargeItem()
        g.session.add_charge_state.originating_authority = authority
        g.session.add_charge_state.statutory_provision = 'Not provided'
        g.session.add_charge_state.schema_version = SCHEMA_VERSION
        g.session.redirect_route = None

    g.session.add_charge_state.charge_type = charge_type
    g.session.commit()

    return redirect(url_for('add_land_charge.get_sub_category'))


def reset_category_info():
    g.session.add_charge_state.charge_type = None
    g.session.add_charge_state.charge_sub_category = None
    g.session.add_charge_state.statutory_provision = 'Not provided'
    g.session.add_charge_state.instrument = None
    g.session.category_confirmation = None
    g.session.category_details = None
    g.session.commit()
