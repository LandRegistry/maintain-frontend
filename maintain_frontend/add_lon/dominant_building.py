from flask import g, render_template, redirect, url_for, current_app, request
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.add_lon.validation.dominant_address_validator import DominantAddressValidator
from maintain_frontend.add_lon.routing.review_router import ReviewRouter


def register_routes(bp):
    bp.add_url_rule('/add-light-obstruction-notice/dominant-building-address',
                    view_func=get_dominant_building_info, methods=['GET'])
    bp.add_url_rule('/add-light-obstruction-notice/dominant-building-address',
                    view_func=post_dominant_building, methods=['POST'])


@requires_permission([Permissions.add_lon])
def get_dominant_building_info():
    if g.session.add_lon_charge_state is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_lon.new"))
        return redirect(url_for("add_lon.new"))

    request_body = {}

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

    current_app.logger.info("Displaying page 'dominant-building.html'")
    return render_template('dominant_building.html',
                           request_body=request_body,
                           submit_url=url_for('add_lon.post_dominant_building'))


@requires_permission([Permissions.add_lon])
def post_dominant_building():
    address_form = request.form

    validation_error_builder = DominantAddressValidator.validate(address_form)

    if validation_error_builder.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template('dominant_building.html',
                               validation_errors=validation_error_builder.errors,
                               validation_summary_heading=validation_error_builder.summary_heading_text,
                               submit_url=url_for('add_lon.post_dominant_building'),
                               request_body=request.form), 400

    current_app.logger.info("Updating session object")

    if address_form['have_address'] == 'Yes':
        charge_address = {
            'unique-property-reference-number': int(address_form['uprn']),
            'postcode': address_form['postcode'],
            'line-1': address_form['address_line_1']
        }
        if address_form['address_line_2']:
            charge_address['line-2'] = address_form['address_line_2']
        if address_form['address_line_3']:
            charge_address['line-3'] = address_form['address_line_3']
        if address_form['address_line_4']:
            charge_address['line-4'] = address_form['address_line_4']
        if address_form['address_line_5']:
            charge_address['line-5'] = address_form['address_line_5']
        if address_form['address_line_6']:
            charge_address['line-6'] = address_form['address_line_6']

        ReviewRouter.update_edited_dominant_address('charge_address', charge_address)
        g.session.add_lon_charge_state.charge_address = charge_address
        g.session.add_lon_charge_state.charge_geographic_description = ''
    else:
        charge_geographic_description = address_form['charge_geographic_description']
        ReviewRouter.update_edited_dominant_address('charge_geographic_description', charge_geographic_description)
        g.session.add_lon_charge_state.charge_address = ''
        g.session.add_lon_charge_state.charge_geographic_description = charge_geographic_description

    g.session.commit()

    return redirect(ReviewRouter.get_redirect_url('add_lon.get_dominant_building_extent'))
