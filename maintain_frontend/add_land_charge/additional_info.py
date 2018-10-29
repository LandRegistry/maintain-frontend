from flask import render_template, redirect, url_for, request, current_app, g
from maintain_frontend.add_land_charge.validation.additional_info_validator import AddChargeAdditionalInfoValidator
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.dependencies.local_authority_api.local_authority_api_service import LocalAuthorityService
from maintain_frontend.add_land_charge.routing.review_router import ReviewRouter
from maintain_frontend.services.field_utilities import has_value_changed


def register_routes(bp):
    bp.add_url_rule('/add-local-land-charge/source-information', view_func=get_additional_info, methods=['GET'])
    bp.add_url_rule('/add-local-land-charge/source-information', view_func=post_additional_info, methods=['POST'])


@requires_permission([Permissions.add_llc])
def get_additional_info():
    current_app.logger.info('Endpoint called')

    if g.session.add_charge_state is None:
        current_app.logger.info('Redirecting to: {}'.format(url_for('add_land_charge.new')))
        return redirect(url_for('add_land_charge.new'))

    current_app.logger.info("Displaying page 'additional_info.html'")
    return render_template('additional_info.html',
                           information=g.session.add_charge_state.further_information_location,
                           reference=g.session.add_charge_state.further_information_reference,
                           source_information_list=get_source_information_list(),
                           submit_url=url_for('add_land_charge.post_additional_info'))


@requires_permission([Permissions.add_llc])
def post_additional_info():
    current_app.logger.info("Endpoint called with additional-info = '{}', reference = '{}'".format(
        request.form.get('additional-info', '').strip(),
        request.form.get('reference', '').strip()
    ))

    if g.session.add_charge_state is None:
        current_app.logger.info('Redirecting to: {}'.format(url_for('add_land_charge.new')))
        return redirect(url_for('add_land_charge.new'))

    information = request.form['additional-info'].strip()
    reference = request.form['reference'].strip()

    current_app.logger.info('Running validation')
    validation_errors = AddChargeAdditionalInfoValidator.validate(information, reference)

    if validation_errors.errors:
        current_app.logger.warning('Validation errors occurred')
        return render_template('additional_info.html',
                               validation_errors=validation_errors.errors,
                               validation_summary_heading=validation_errors.summary_heading_text,
                               information=information,
                               submit_url=url_for('add_land_charge.post_additional_info'),
                               source_information_list=get_source_information_list(),
                               reference=reference), 400

    current_app.logger.info('Updating session object')
    ReviewRouter.update_edited_field('further_information_location', information)
    if has_value_changed(g.session.add_charge_state.further_information_reference, reference):
        ReviewRouter.update_edited_field('further_information_reference', reference)
        g.session.add_charge_state.further_information_reference = reference

    g.session.add_charge_state.further_information_location = information
    g.session.commit()

    return redirect(ReviewRouter.get_redirect_url('add_land_charge.get_charge_description'))


def get_source_information_list():
    source_information_list = None

    if g.application_permissions.view_source_information in g.session.user.permissions:
        current_app.logger.info('User has permission to view source information, retrieving')
        local_authority_service = LocalAuthorityService(current_app.config)
        source_information_list = local_authority_service.get_source_information_for_organisation(
            g.session.user.organisation)
        source_information_list = list(map(lambda source: source['source-information'], source_information_list))

    return source_information_list
