from flask import g, render_template, redirect, url_for, current_app, request
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder
from maintain_frontend.add_lon.routing.review_router import ReviewRouter


def register_routes(bp):
    bp.add_url_rule('/add-light-obstruction-notice/interest-in-land', view_func=get_land_interest, methods=['GET'])
    bp.add_url_rule('/add-light-obstruction-notice/interest-in-land', view_func=post_land_interest, methods=['POST'])


@requires_permission([Permissions.add_lon])
def get_land_interest():
    if g.session.add_lon_charge_state is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_lon.new"))
        return redirect(url_for("add_lon.new"))

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
                           request_body=g.session.add_lon_charge_state.servient_land_interest_description,
                           submit_url=url_for("add_lon.post_land_interest"),
                           checked=checked)


@requires_permission([Permissions.add_lon])
def post_land_interest():
    if g.session.add_lon_charge_state is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_lon.new"))
        return redirect(url_for("add_lon.new"))

    current_app.logger.info("Running validation")

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
                               submit_url=url_for("add_lon.post_land_interest"),
                               validation_errors=validation_error_builder.errors,
                               validation_summary_heading=validation_error_builder.summary_heading_text,
                               checked=checked,
                               request_body=land_interest), 400

    current_app.logger.info("Updating session object")
    ReviewRouter.update_edited_field('servient_land_interest_description', land_interest)

    g.session.add_lon_charge_state.servient_land_interest_description = land_interest
    g.session.commit()

    return redirect(ReviewRouter.get_redirect_url("add_lon.get_upload_lon_documents"))
