import json

from flask import g, render_template, request, redirect, url_for, current_app

from maintain_frontend.add_land_charge.validation.address_for_charge_validator import AddressForChargeValidator
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.decorators import requires_permission
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.services.address_converter import AddressConverter
from maintain_frontend.services.charge_id_services import calc_display_id


def register_routes(bp):
    bp.add_url_rule('/address-for-charge', view_func=get_address_for_charge, methods=['GET'])
    bp.add_url_rule('/address-for-charge', view_func=post_address_for_charge, methods=['POST'])


@requires_permission([Permissions.vary_llc])
def get_address_for_charge():
    """Loads the page to gather more information about a location.


    :return: more information template
    """
    current_app.logger.info("Endpoint called")
    if g.session.add_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)
    current_app.logger.info("Rendering response")
    if g.session.add_charge_state.charge_geographic_description:
        return render_template('address_for_charge.html',
                               charge_geographic_description=g.session.add_charge_state.charge_geographic_description,
                               has_address="No",
                               submit_url=url_for("modify_land_charge.post_address_for_charge"))
    else:
        return render_template('address_for_charge.html',
                               charge_address=AddressConverter.get_display_address(
                                   g.session.add_charge_state.charge_address),
                               postcode=g.session.add_charge_state.charge_address['postcode'],
                               has_address="ProvideAddress",
                               submit_url=url_for("modify_land_charge.post_address_for_charge"))


@requires_permission([Permissions.vary_llc])
def post_address_for_charge():
    """Save more information about the location to session and move to the next screen.


    :return: redirect to the next screen in the flow
    """
    current_app.logger.info("Endpoint called")
    if g.session.add_charge_state is None:
        raise ApplicationError(500)

    has_address = request.form.get('has-address')
    charge_geographic_description = request.form.get('charge-geographic-description')
    selected_address = request.form.get('selected-address')

    current_app.logger.info("Validating location information")
    validation_errors = AddressForChargeValidator.validate(has_address, selected_address,
                                                           charge_geographic_description)
    if validation_errors.errors:
        current_app.logger.warning("Validation errors present - Rendering page with validation errors")
        return render_template('address_for_charge.html',
                               validation_errors=validation_errors.errors,
                               validation_summary_heading=validation_errors.summary_heading_text,
                               charge_geographic_description=charge_geographic_description,
                               has_address=has_address,
                               submit_url=url_for("modify_land_charge.post_address_for_charge")), 400

    current_app.logger.info("Field values validated - Updating session charge")
    edited = False

    if selected_address:
        selected_address = json.loads(selected_address)
        new_address = AddressConverter.to_charge_address(selected_address)
        if g.session.add_charge_state.charge_address != new_address:
            g.session.add_charge_state.charge_address = new_address
            g.session.add_charge_state.charge_geographic_description = None
            g.session.edited_fields.append('location_info')
            edited = True

    elif charge_geographic_description:
        if g.session.add_charge_state.charge_geographic_description != charge_geographic_description:
            g.session.add_charge_state.charge_geographic_description = charge_geographic_description
            g.session.add_charge_state.charge_address = None
            g.session.edited_fields.append('location_info')
            edited = True

    if edited:
        g.session.commit()

    charge_display_id = calc_display_id(g.session.add_charge_state.local_land_charge)
    current_app.logger.info(
        "Session charge updated - Redirecting back to modify_land_charge with local_land_charge='{}'"
        .format(charge_display_id)
    )
    return redirect(url_for("modify_land_charge.modify_land_charge", local_land_charge=charge_display_id))
