from flask import g, redirect, url_for, render_template, current_app, request
from maintain_frontend.add_land_charge.routing.review_router import ReviewRouter
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.decorators import requires_permission
from maintain_frontend.add_land_charge.validation.location_confirmation_validator import LocationConfirmationValidator


def register_routes(bp):
    bp.add_url_rule('/add-local-land-charge/location-confirmation',
                    view_func=get_location_confirmation,
                    methods=['GET'])
    bp.add_url_rule('/add-local-land-charge/location-confirmation',
                    view_func=post_location_confirmation,
                    methods=['POST'])


@requires_permission([Permissions.add_llc])
def get_location_confirmation():
    current_app.logger.info('Endpoint called')

    if g.session.add_charge_state is None:
        current_app.logger.info('Redirecting to: {}'.format(url_for('add_land_charge.new')))
        return redirect(url_for('add_land_charge.new'))

    if g.session.add_charge_state.geometry is None:
        return redirect(url_for('add_land_charge.get_location'))

    current_app.logger.info("Displaying page 'location_confirmation.html'")
    address_selected = False
    if request.args.get('address_selected') is not None:
        address_selected = request.args.get('address_selected')

    return render_template('location_confirmation.html',
                           submit_url=url_for('add_land_charge.post_location_confirmation',
                                              address_selected=address_selected))


@requires_permission([Permissions.add_llc])
def post_location_confirmation():
    current_app.logger.info('Endpoint called')

    if g.session.add_charge_state is None:
        current_app.logger.info('Redirecting to: {}'.format(url_for('add_land_charge.new')))
        return redirect(url_for('add_land_charge.new'))

    if g.session.add_charge_state.geometry is None:
        return redirect(url_for('add_land_charge.get_location'))

    confirmation = request.form.get('location-confirmation')

    current_app.logger.info('Running validation')
    validation_errors = LocationConfirmationValidator.validate(confirmation, 'add')

    if validation_errors.errors:
        current_app.logger.warning('Validation errors occurred')
        return render_template(
            'location_confirmation.html',
            validation_errors=validation_errors.errors,
            validation_summary_heading=validation_errors.summary_heading_text,
            submit_url=url_for('add_land_charge.post_location_confirmation')
        ), 400

    address_selected = request.args.get('address_selected')

    g.session.charge_added_outside_users_authority = True
    g.session.commit()

    if address_selected == 'True':
        return redirect(ReviewRouter.get_redirect_url('add_land_charge.get_address_confirmation'))
    else:
        return redirect(ReviewRouter.get_redirect_url('add_land_charge.get_address_for_charge'))
