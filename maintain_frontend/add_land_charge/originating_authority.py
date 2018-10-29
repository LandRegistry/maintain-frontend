from flask import render_template, url_for, g, redirect, request, current_app
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.add_land_charge.validation.authority_validator import AuthorityValidator
from maintain_frontend.add_land_charge.routing.review_router import ReviewRouter
from maintain_frontend.dependencies.local_authority_api.local_authority_api_service import LocalAuthorityService


def register_routes(bp):
    bp.add_url_rule('/add-local-land-charge/who-are-you-adding-for',
                    view_func=get_originating_authority_page, methods=['GET'])
    bp.add_url_rule('/add-local-land-charge/who-are-you-adding-for',
                    view_func=post_originating_authority_page, methods=['POST'])


@requires_permission([Permissions.add_llc])
def get_originating_authority_page():
    if g.session.add_charge_state is None or g.session.adding_charge_for_other_authority is False:
        current_app.logger.info("Redirecting to: %s", url_for("add_land_charge.new_behalf_of_authority"))
        return redirect(url_for("add_land_charge.new_behalf_of_authority"))

    local_authority_service = LocalAuthorityService(current_app.config)
    response = local_authority_service.get_organisations()
    authorities = list(map(lambda org: org.get('title'), response))

    current_app.logger.info("Displaying page 'charge_type.html'")
    return render_template('originating_authority.html',
                           authorities=authorities,
                           submit_url=url_for('add_land_charge.post_originating_authority_page'))


@requires_permission([Permissions.add_llc])
def post_originating_authority_page():
    authority = request.form.get('authority-search-field')

    local_authority_service = LocalAuthorityService(current_app.config)
    response = local_authority_service.get_organisations()
    authorities = list(map(lambda org: org.get('title'), response))

    current_app.logger.info("Running validation")
    validation_errors = AuthorityValidator.validate(authority, authorities)

    if validation_errors.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template(
            'originating_authority.html',
            authorities=authorities,
            validation_errors=validation_errors.errors,
            validation_summary_heading=validation_errors.summary_heading_text,
            submit_url=url_for('add_land_charge.post_originating_authority_page')), 400

    ReviewRouter.update_edited_field('originating_authority', authority)
    g.session.add_charge_state.originating_authority = authority
    g.session.commit()

    return redirect(ReviewRouter.get_redirect_url('add_land_charge.get_charge_type'))
