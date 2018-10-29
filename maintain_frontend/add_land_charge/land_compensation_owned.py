from flask import render_template, redirect, url_for, request, g, current_app
from maintain_frontend.add_land_charge.validation.land_compensation_owned_validator \
    import LandCompensationOwnedValidator
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.add_land_charge.routing.review_router import ReviewRouter

INTEREST_MAY_BE_PAYABLE = 'Interest may be payable'


def register_routes(bp):
    bp.add_url_rule('/add-local-land-charge/how-is-land-owned',
                    view_func=get_land_compensation_owned, methods=['GET'])
    bp.add_url_rule('/add-local-land-charge/how-is-land-owned',
                    view_func=post_land_compensation_owned, methods=['POST'])


@requires_permission([Permissions.add_llc])
def get_land_compensation_owned():
    if g.session.add_charge_state is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_land_charge.new"))
        return redirect(url_for("add_land_charge.new"))

    land_owned_indicator = None
    land_owned_other = None

    if g.session.add_charge_state.land_capacity_description:
        if g.session.add_charge_state.land_capacity_description not in ['Freehold', 'Leasehold']:
            land_owned_indicator = "Other"
            land_owned_other = g.session.add_charge_state.land_capacity_description
        else:
            land_owned_indicator = g.session.add_charge_state.land_capacity_description
            land_owned_other = None

    request_body = {
        'land-owned-indicator': land_owned_indicator,
        'land-owned-other': land_owned_other
    }

    current_app.logger.info("Displaying page 'land_compensation_owned.html'")
    return render_template('land_compensation_owned.html',
                           request_body=request_body,
                           submit_url=url_for('add_land_charge.post_land_compensation_owned'))


@requires_permission([Permissions.add_llc])
def post_land_compensation_owned():
    current_app.logger.info("Endpoint called with land-owned-indicator = '%s' and land-owned-other = '%s'",
                            request.form.get('land-owned-indicator', ''), request.form.get('land-owned-other', ''))
    if g.session.add_charge_state is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_land_charge.new"))
        return redirect(url_for("add_land_charge.new"))

    land_owned_indicator = request.form.get('land-owned-indicator', '')
    land_owned_other = request.form.get('land-owned-other', '').strip()

    current_app.logger.info("Running validation")
    validation_errors = LandCompensationOwnedValidator.validate(land_owned_indicator, land_owned_other)
    if validation_errors.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template(
            'land_compensation_owned.html',
            validation_errors=validation_errors.errors,
            validation_summary_heading=validation_errors.summary_heading_text,
            request_body=request.form,
            submit_url=url_for('add_land_charge.post_land_compensation_owned')
        ), 400

    if land_owned_indicator == "Other":
        ReviewRouter.update_edited_field('land_capacity_description', land_owned_other)
        g.session.add_charge_state.land_capacity_description = land_owned_other
    else:
        ReviewRouter.update_edited_field('land_capacity_description', land_owned_indicator)
        g.session.add_charge_state.land_capacity_description = land_owned_indicator

    current_app.logger.info("Updating session object with land capacity description: '%s'",
                            g.session.add_charge_state.land_capacity_description)

    g.session.commit()

    current_app.logger.info("Redirecting to next step: %s",
                            ReviewRouter.get_redirect_url("add_land_charge.get_charge_date"))
    return redirect(ReviewRouter.get_redirect_url("add_land_charge.get_charge_date"))
