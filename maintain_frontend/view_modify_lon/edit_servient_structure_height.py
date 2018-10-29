from flask import render_template, redirect, url_for, request, g, current_app
from maintain_frontend.services.charge_id_services import calc_display_id
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.add_lon.validation.servient_structure_height_validator import ServientStructureHeightValidator


def register_routes(bp):
    bp.add_url_rule('/servient-structure-height', view_func=edit_servient_structure_height_get, methods=['GET'])
    bp.add_url_rule('/servient-structure-height', view_func=edit_servient_structure_height_post, methods=['POST'])


@requires_permission([Permissions.vary_lon])
def edit_servient_structure_height_get():
    if g.session.add_lon_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)

    structure_position_and_dimension = g.session.add_lon_charge_state.structure_position_and_dimension

    request_body = {}

    if 'height' in structure_position_and_dimension:
        if structure_position_and_dimension['height'] == "Unlimited height":
            request_body['measurement'] = "Unlimited height"
        else:
            request_body['measurement'] = "I have measurements for the height"
            request_body['height'] = structure_position_and_dimension['height']
            request_body['unit'] = structure_position_and_dimension['units']

    return render_template('servient_structure_height.html',
                           submit_url=url_for('modify_lon.edit_servient_structure_height_post'),
                           request_body=request_body)


@requires_permission([Permissions.vary_lon])
def edit_servient_structure_height_post():
    if g.session.add_lon_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)

    servient_structure_height_form = request.form
    measurement = servient_structure_height_form.get('measurement')
    height = servient_structure_height_form.get('height')
    unit = servient_structure_height_form.get('unit')

    validation_error_builder = ServientStructureHeightValidator.validate(measurement, height, unit)

    if validation_error_builder.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template('servient_structure_height.html',
                               validation_errors=validation_error_builder.errors,
                               validation_summary_heading=validation_error_builder.summary_heading_text,
                               submit_url=url_for('modify_lon.edit_servient_structure_height_post'),
                               request_body=request.form), 400

    current_app.logger.info("Updating session object")

    structure_position_and_dimension = g.session.add_lon_charge_state.structure_position_and_dimension

    edited = False
    if measurement == "Unlimited height":
        if 'height' not in g.session.add_lon_charge_state.structure_position_and_dimension:
            edited = True
        else:
            if g.session.add_lon_charge_state.structure_position_and_dimension["height"] != "Unlimited height":
                edited = True
        structure_position_and_dimension["height"] = measurement
        if 'units' in structure_position_and_dimension:
            del(structure_position_and_dimension['units'])
    else:
        if 'height' not in g.session.add_lon_charge_state.structure_position_and_dimension:
            edited = True
        else:
            if g.session.add_lon_charge_state.structure_position_and_dimension["height"] != height \
                    or g.session.add_lon_charge_state.structure_position_and_dimension["units"] != unit:
                edited = True
        structure_position_and_dimension["height"] = height
        structure_position_and_dimension["units"] = unit

    if edited:
        g.session.add_lon_charge_state.structure_position_and_dimension = structure_position_and_dimension
        g.session.edited_fields['structure-dimension'] = 'Height - planned development'
        g.session.commit()

    charge_display_id = calc_display_id(g.session.add_lon_charge_state.local_land_charge)
    current_app.logger.info(
        "Session charge updated - Redirecting back to modify_land_charge with local_land_charge='{}'".format(
            charge_display_id
        )
    )

    return redirect(url_for("modify_lon.modify_lon_details_get", charge_id=charge_display_id))
