from flask import render_template, redirect, url_for, request, g, current_app
from maintain_frontend.services.charge_id_services import calc_display_id
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.add_lon.validation.servient_structure_position_validator \
    import ServientStructurePositionValidator


def register_routes(bp):
    bp.add_url_rule('/servient-structure-coverage',
                    view_func=edit_servient_structure_position_get, methods=['GET'])
    bp.add_url_rule('/servient-structure-coverage',
                    view_func=edit_servient_structure_position_post, methods=['POST'])


@requires_permission([Permissions.vary_lon])
def edit_servient_structure_position_get():
    if g.session.add_lon_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)

    structure_position_and_dimension = g.session.add_lon_charge_state.structure_position_and_dimension

    request_body = {}

    if structure_position_and_dimension['extent-covered'] == 'All of the extent':
        request_body['extent'] = "All of the extent"
    else:
        request_body['extent'] = "Part of the extent"
        request_body['part_extent_detail'] = structure_position_and_dimension['part-explanatory-text']

    return render_template('servient_structure_position.html',
                           submit_url=url_for('modify_lon.edit_servient_structure_position_post'),
                           request_body=request_body)


@requires_permission([Permissions.vary_lon])
def edit_servient_structure_position_post():
    if g.session.add_lon_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)

    extent = request.form.get('extent')
    part_extent_detail = request.form.get('part_extent_detail')

    validation_error_builder = ServientStructurePositionValidator.validate(extent, part_extent_detail)

    if validation_error_builder.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template('servient_structure_position.html',
                               validation_errors=validation_error_builder.errors,
                               validation_summary_heading=validation_error_builder.summary_heading_text,
                               submit_url=url_for('modify_lon.edit_servient_structure_position_post'),
                               request_body=request.form), 400

    position_and_dimension = g.session.add_lon_charge_state.structure_position_and_dimension

    edited = False
    if extent == "All of the extent":
        if 'part-explanatory-text' in position_and_dimension:
            edited = True
            del(position_and_dimension['part-explanatory-text'])
    else:
        if position_and_dimension["extent-covered"] != extent\
                or 'part-explanatory-text' in position_and_dimension \
                and position_and_dimension["part-explanatory-text"] != part_extent_detail:
            edited = True
        position_and_dimension["part-explanatory-text"] = part_extent_detail

    position_and_dimension['extent-covered'] = extent

    if edited:
        g.session.add_lon_charge_state.structure_position_and_dimension = position_and_dimension
        g.session.edited_fields['structure-position'] = 'Extent - planned development'
        g.session.commit()

    charge_display_id = calc_display_id(g.session.add_lon_charge_state.local_land_charge)
    current_app.logger.info(
        "Session charge updated - Redirecting back to modify_land_charge with local_land_charge='{}'".format(
            charge_display_id
        )
    )

    return redirect(url_for("modify_lon.modify_lon_details_get", charge_id=charge_display_id))
