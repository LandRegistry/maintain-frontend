import json
from flask import render_template, redirect, url_for, request, current_app, g
from maintain_frontend.decorators import requires_permission
from maintain_frontend.services.address_converter import AddressConverter
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.add_land_charge.validation.address_for_charge_validator import AddressForChargeValidator


def register_routes(bp):
    bp.add_url_rule('/add-local-land-charge/address-confirmation', view_func=get_address_confirmation, methods=['GET'])
    bp.add_url_rule('/add-local-land-charge/address-confirmation',
                    view_func=post_address_confirmation, methods=['POST'])


@requires_permission([Permissions.add_llc])
def get_address_confirmation():
    current_app.logger.info('Endpoint called')
    if g.session.add_charge_state is None:
        current_app.logger.info('Redirecting to: {}'.format(url_for('add_land_charge.new')))
        return redirect(url_for('add_land_charge.new'))

    return render_template('address_confirmation.html',
                           submit_url=url_for('add_land_charge.post_address_confirmation'))


@requires_permission([Permissions.add_llc])
def post_address_confirmation():

    if g.session.add_charge_state is None:
        current_app.logger.info('Redirecting to: {}'.format(url_for('add_land_charge.new')))
        return redirect(url_for('add_land_charge.new'))

    has_address = request.form.get('has-address')
    charge_geographic_description = request.form.get('charge-geographic-description')
    selected_address = None

    if has_address == 'Yes':
        selected_address = g.session.previously_selected_address
    if has_address == 'ProvideAddress' and request.form.get('selected-address'):
        selected_address = json.loads(request.form.get('selected-address'))

    current_app.logger.info("Running validation")
    validation_errors = AddressForChargeValidator.validate(has_address, selected_address,
                                                           charge_geographic_description)
    if validation_errors.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template(
            'address_confirmation.html',
            validation_errors=validation_errors.errors,
            validation_summary_heading=validation_errors.summary_heading_text,
            has_address=has_address,
            charge_geographic_description=charge_geographic_description,
            submit_url=url_for('add_land_charge.post_address_confirmation')
        ), 400

    if selected_address:
        g.session.add_charge_state.charge_address = AddressConverter.to_charge_address(selected_address)
        g.session.add_charge_state.charge_geographic_description = None
        g.session.previously_selected_address = None

    elif charge_geographic_description:
        g.session.add_charge_state.charge_geographic_description = charge_geographic_description
        g.session.add_charge_state.charge_address = None
        g.session.previously_selected_address = None

    g.session.commit()
    return redirect(url_for('add_land_charge.get_expiry'))
