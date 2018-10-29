from flask import g, render_template, redirect, url_for, current_app, request
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.add_lon.validation.servient_structure_height_validator import ServientStructureHeightValidator
from maintain_frontend.add_lon.routing.review_router import ReviewRouter
from copy import copy


def register_routes(bp):
    bp.add_url_rule('/add-light-obstruction-notice/servient-structure-height',
                    view_func=get_servient_structure_height, methods=['GET'])
    bp.add_url_rule('/add-light-obstruction-notice/servient-structure-height',
                    view_func=post_servient_structure_height, methods=['POST'])


@requires_permission([Permissions.add_lon])
def get_servient_structure_height():
    if g.session.add_lon_charge_state is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_lon.new"))
        return redirect(url_for("add_lon.new"))

    request_body = {}

    if g.session.add_lon_charge_state.structure_position_and_dimension and \
            'height' in g.session.add_lon_charge_state.structure_position_and_dimension:

        structure_position_and_dimension = g.session.add_lon_charge_state.structure_position_and_dimension

        if structure_position_and_dimension['height'] == "Unlimited height":
            request_body['measurement'] = "Unlimited height"
        else:
            request_body['measurement'] = "I have measurements for the height"
            request_body['height'] = structure_position_and_dimension['height']
            request_body['unit'] = structure_position_and_dimension['units']

    current_app.logger.info("Displaying page 'servient_structure_height.html'")
    return render_template('servient_structure_height.html',
                           submit_url=url_for('add_lon.post_servient_structure_height'),
                           request_body=request_body)


@requires_permission([Permissions.add_lon])
def post_servient_structure_height():
    if g.session.add_lon_charge_state is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_lon.new"))
        return redirect(url_for("add_lon.new"))

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
                               submit_url=url_for('add_lon.post_servient_structure_height'),
                               request_body=request.form), 400

    current_app.logger.info("Updating session object")

    if g.session.add_lon_charge_state.structure_position_and_dimension:
        position_and_dimension = copy(g.session.add_lon_charge_state.structure_position_and_dimension)
    else:
        position_and_dimension = {
            "height": ""
        }

    if measurement == "Unlimited height":
        position_and_dimension["height"] = measurement
        if 'units' in position_and_dimension:
            del(position_and_dimension['units'])
    else:
        position_and_dimension["height"] = height
        position_and_dimension["units"] = unit

    ReviewRouter.update_edited_height_or_position(position_and_dimension)
    g.session.add_lon_charge_state.structure_position_and_dimension = position_and_dimension
    g.session.commit()

    return redirect(ReviewRouter.get_redirect_url('add_lon.get_servient_structure_position'))
