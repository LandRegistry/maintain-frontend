from flask import render_template, redirect, url_for, request, g, current_app
from maintain_frontend.services.charge_id_services import calc_display_id
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


def register_routes(bp):
    bp.add_url_rule('/interest-in-land', view_func=edit_lon_land_interest_get, methods=['GET'])
    bp.add_url_rule('/interest-in-land', view_func=edit_lon_land_interest_post, methods=['POST'])


@requires_permission([Permissions.vary_lon])
def edit_lon_land_interest_get():
    if g.session.add_lon_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)

    # If the servient land Interest is on of the existing options, set the checked variable, otherwise set other
    # the variable is used in the template to "select" the correct option, including other, and the textarea
    if (g.session.add_lon_charge_state.servient_land_interest_description == "Freehold owner"):
        checked = "Freehold owner"
    elif (g.session.add_lon_charge_state.servient_land_interest_description ==
          "Tenant for a term of which over 7 years remain unexpired"):
                checked = "Tenant for a term of which over 7 years remain unexpired"
    elif (g.session.add_lon_charge_state.servient_land_interest_description == "Mortgagee in possession"):
        checked = "Mortgagee in possession"
    elif g.session.add_lon_charge_state.servient_land_interest_description is None:
        checked = ""
    else:
        checked = "Other"

    current_app.logger.info("Displaying page 'lon_land_interest.html'")
    return render_template('lon_land_interest.html',
                           submit_url=url_for('modify_lon.edit_lon_land_interest_post'),
                           request_body=g.session.add_lon_charge_state.servient_land_interest_description,
                           checked=checked)


@requires_permission([Permissions.vary_lon])
def edit_lon_land_interest_post():
    if g.session.add_lon_charge_state is None:
        current_app.logger.error("Charge state not found in session - Returning error")
        raise ApplicationError(500)

    # Different validation and error messages are required for other instead of the existing options.
    land_interest = request.form.get("servient-land-interest-description")
    if land_interest == "Other":
        land_interest = request.form.get("servient-land-interest-detail")
        validation_error_builder = ValidationErrorBuilder()
        FieldValidator(land_interest, 'servient-land-interest-detail', 'Land Interest', validation_error_builder,
                       summary_message="There are errors on the page. Describe the interest in land",
                       inline_message="Explain how the person applying for the light obstruction notice "
                       "owns or uses the land") \
            .is_required()
        checked = "Other"
    else:
        validation_error_builder = ValidationErrorBuilder()
        FieldValidator(land_interest, 'servient-land-interest-description', 'Land Interest', validation_error_builder,
                       summary_message="Choose one",
                       inline_message="Choose one") \
            .is_required()
        checked = request.form.get("servient-land-interest-description")

    if validation_error_builder.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template('lon_land_interest.html',
                               submit_url=url_for("modify_lon.edit_lon_land_interest_post"),
                               validation_errors=validation_error_builder.errors,
                               validation_summary_heading=validation_error_builder.summary_heading_text,
                               checked=checked,
                               request_body=land_interest), 400

    if g.session.add_lon_charge_state.servient_land_interest_description != land_interest:
        g.session.add_lon_charge_state.servient_land_interest_description = land_interest
        g.session.edited_fields['servient-land-interest-description'] = 'Interest'
        g.session.commit()

    charge_display_id = calc_display_id(g.session.add_lon_charge_state.local_land_charge)
    current_app.logger.info(
        "Session charge updated - Redirecting back to modify_land_charge with local_land_charge='{}'".format(
            charge_display_id
        )
    )

    return redirect(url_for("modify_lon.modify_lon_details_get", charge_id=charge_display_id))
