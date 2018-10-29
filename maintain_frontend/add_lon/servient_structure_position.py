from flask import g, render_template, redirect, url_for, current_app, request
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.add_lon.validation.servient_structure_position_validator \
    import ServientStructurePositionValidator
from maintain_frontend.add_lon.routing.review_router import ReviewRouter
from copy import copy


def register_routes(bp):
    bp.add_url_rule('/add-light-obstruction-notice/servient-structure-coverage',
                    view_func=get_servient_structure_position, methods=['GET'])
    bp.add_url_rule('/add-light-obstruction-notice/servient-structure-coverage',
                    view_func=post_servient_structure_position, methods=['POST'])


@requires_permission([Permissions.add_lon])
def get_servient_structure_position():
    if g.session.add_lon_charge_state is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_lon.new"))
        return redirect(url_for("add_lon.new"))

    request_body = {}

    if g.session.add_lon_charge_state.structure_position_and_dimension and \
            'extent-covered' in g.session.add_lon_charge_state.structure_position_and_dimension:

        structure_position_and_dimension = g.session.add_lon_charge_state.structure_position_and_dimension

        if structure_position_and_dimension['extent-covered'] == 'All of the extent':
            request_body['extent'] = "All of the extent"
        else:
            request_body['extent'] = "Part of the extent"
            request_body['part_extent_detail'] = structure_position_and_dimension['part-explanatory-text']

    current_app.logger.info("Displaying page 'servient_structure_position.html'")
    return render_template('servient_structure_position.html',
                           submit_url=url_for('add_lon.post_servient_structure_position'),
                           request_body=request_body)


@requires_permission([Permissions.add_lon])
def post_servient_structure_position():
    if g.session.add_lon_charge_state is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_lon.new"))
        return redirect(url_for("add_lon.new"))

    extent = request.form.get('extent')
    part_extent_detail = request.form.get('part_extent_detail')

    validation_error_builder = ServientStructurePositionValidator.validate(extent, part_extent_detail)

    if validation_error_builder.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template('servient_structure_position.html',
                               validation_errors=validation_error_builder.errors,
                               validation_summary_heading=validation_error_builder.summary_heading_text,
                               submit_url=url_for('add_lon.post_servient_structure_position'),
                               request_body=request.form), 400

    position_and_dimension = copy(g.session.add_lon_charge_state.structure_position_and_dimension)
    position_and_dimension['extent-covered'] = extent
    if extent == "Part of the extent":
        position_and_dimension["part-explanatory-text"] = part_extent_detail
    elif "part-explanatory-text" in position_and_dimension:
        del position_and_dimension["part-explanatory-text"]

    ReviewRouter.update_edited_height_or_position(position_and_dimension)
    g.session.add_lon_charge_state.structure_position_and_dimension = position_and_dimension
    g.session.commit()

    return redirect(ReviewRouter.get_redirect_url('add_lon.get_review'))
