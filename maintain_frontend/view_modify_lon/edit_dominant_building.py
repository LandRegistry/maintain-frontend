from flask import render_template, redirect, url_for, request, g, current_app
from maintain_frontend.services.charge_id_services import calc_display_id
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.add_lon.validation.dominant_address_validator import DominantAddressValidator


def register_routes(bp):
    bp.add_url_rule('/dominant-building-address', view_func=edit_dominant_building_get, methods=['GET'])
    bp.add_url_rule('/dominant-building-address', view_func=edit_dominant_building_post, methods=['POST'])


@requires_permission([Permissions.vary_lon])
def edit_dominant_building_get():
    if g.session.add_lon_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)

    if g.session.add_lon_charge_state.charge_address:
        dominant_address = g.session.add_lon_charge_state.charge_address

        request_body = {
            'address_line_1': dominant_address['line-1'],
            'postcode': dominant_address['postcode']
        }

        if 'line-2' in dominant_address:
            request_body['address_line_2'] = dominant_address['line-2']
        if 'line-3' in dominant_address:
            request_body['address_line_3'] = dominant_address['line-3']
        if 'line-4' in dominant_address:
            request_body['address_line_4'] = dominant_address['line-4']
        if 'line-5' in dominant_address:
            request_body['address_line_5'] = dominant_address['line-5']
        if 'line-6' in dominant_address:
            request_body['address_line_6'] = dominant_address['line-6']
        if 'unique-property-reference-number' in dominant_address:
            request_body['uprn'] = dominant_address['unique-property-reference-number']

    elif g.session.add_lon_charge_state.charge_geographic_description:
        request_body = {
            'charge_geographic_description': g.session.add_lon_charge_state.charge_geographic_description
        }

    current_app.logger.info("Rendering template")
    return render_template('dominant_building.html', submit_url=url_for('modify_lon.edit_dominant_building_post'),
                           request_body=request_body)


@requires_permission([Permissions.vary_lon])
def edit_dominant_building_post():
    if g.session.add_lon_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)

    validation_error_builder = DominantAddressValidator.validate(request.form)

    if validation_error_builder.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template('dominant_building.html',
                               validation_errors=validation_error_builder.errors,
                               validation_summary_heading=validation_error_builder.summary_heading_text,
                               submit_url=url_for('modify_lon.edit_dominant_building_post'),
                               request_body=request.form), 400

    if request.form['have_address'] == 'Yes':
        charge_address = {
            'unique-property-reference-number': int(request.form['uprn']),
            'postcode': request.form['postcode'],
            'line-1': request.form['address_line_1']
        }
        if request.form['address_line_2']:
            charge_address['line-2'] = request.form['address_line_2']
        if request.form['address_line_3']:
            charge_address['line-3'] = request.form['address_line_3']
        if request.form['address_line_4']:
            charge_address['line-4'] = request.form['address_line_4']
        if request.form['address_line_5']:
            charge_address['line-5'] = request.form['address_line_5']
        if request.form['address_line_6']:
            charge_address['line-6'] = request.form['address_line_6']

        if charge_address != g.session.add_lon_charge_state.charge_address:
            if 'charge_geographic_description' in g.session.edited_fields:
                del g.session.edited_fields['charge_geographic_description']

            current_app.logger.info('Adding charge-address field to edited_fields')
            g.session.edited_fields['charge-address'] = 'Dominant address'

        g.session.add_lon_charge_state.charge_address = charge_address
        g.session.add_lon_charge_state.charge_geographic_description = ''
    else:
        charge_geographic_description = request.form['charge_geographic_description']

        if charge_geographic_description != g.session.add_lon_charge_state.charge_geographic_description:
            if 'charge-address' in g.session.edited_fields:
                del g.session.edited_fields['charge-address']

            current_app.logger.info('Adding charge_geographic_description field to edited_fields')
            g.session.edited_fields['charge_geographic_description'] = 'Dominant address'

        g.session.add_lon_charge_state.charge_address = ''
        g.session.add_lon_charge_state.charge_geographic_description = charge_geographic_description

    current_app.logger.info("Updating session object")
    g.session.commit()

    charge_display_id = calc_display_id(g.session.add_lon_charge_state.local_land_charge)

    current_app.logger.info(
        "Session charge updated - Redirecting back to modify_lon with charge_id='{}'".format(charge_display_id)
    )

    return redirect(url_for("modify_lon.modify_lon_details_get", charge_id=charge_display_id))
