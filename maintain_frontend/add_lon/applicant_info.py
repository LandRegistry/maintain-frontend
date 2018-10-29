from flask import g, render_template, redirect, url_for, current_app, request
from maintain_frontend.decorators import requires_permission
from maintain_frontend.dependencies.country_register.country_register_service import get_sorted_countries
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.add_lon.validation.applicant_info_validator import ApplicantInfoValidator
from maintain_frontend.add_lon.routing.review_router import ReviewRouter
from maintain_frontend.services.address_converter import AddressConverter


def register_routes(bp):
    bp.add_url_rule('/add-light-obstruction-notice/who-is-applying', view_func=get_applicant_info, methods=['GET'])
    bp.add_url_rule('/add-light-obstruction-notice/who-is-applying', view_func=post_applicant_info, methods=['POST'])


@requires_permission([Permissions.add_lon])
def get_applicant_info():
    if g.session.add_lon_charge_state is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_lon.new"))
        return redirect(url_for("add_lon.new"))

    request_body = {}

    if g.session.add_lon_charge_state.applicant_address:
        applicant_address = g.session.add_lon_charge_state.applicant_address

        request_body = {
            'applicant_name': g.session.add_lon_charge_state.applicant_name,
            'address_line_1': applicant_address['line-1'],
            'country': applicant_address['country']
        }

        if 'line-2' in applicant_address:
            request_body['address_line_2'] = applicant_address['line-2']
        if 'line-3' in applicant_address:
            request_body['address_line_3'] = applicant_address['line-3']
        if 'line-4' in applicant_address:
            request_body['address_line_4'] = applicant_address['line-4']
        if 'line-5' in applicant_address:
            request_body['address_line_5'] = applicant_address['line-5']
        if 'line-6' in applicant_address:
            request_body['address_line_6'] = applicant_address['line-6']
        if 'postcode' in applicant_address:
            request_body['postcode'] = applicant_address['postcode']

    current_app.logger.info("Displaying page 'applicant_info.html'")
    return render_template('applicant_info.html',
                           request_body=request_body,
                           country_list=get_sorted_countries(),
                           submit_url=url_for('add_lon.post_applicant_info'))


@requires_permission([Permissions.add_lon])
def post_applicant_info():
    address_form = request.form

    current_app.logger.info("Running validation")
    validation_error_builder = ApplicantInfoValidator.validate(address_form)

    if validation_error_builder.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template('applicant_info.html',
                               validation_errors=validation_error_builder.errors,
                               validation_summary_heading=validation_error_builder.summary_heading_text,
                               submit_url=url_for('add_lon.post_applicant_info'),
                               country_list=get_sorted_countries(),
                               request_body=request.form), 400

    applicant_address = AddressConverter.condense_address(address_form)
    applicant_name = address_form.get('applicant_name')

    current_app.logger.info("Updating session object")
    ReviewRouter.update_edited_field('applicant_name', applicant_name)
    ReviewRouter.update_edited_field('applicant_address', applicant_address)

    g.session.add_lon_charge_state.applicant_name = applicant_name
    g.session.add_lon_charge_state.applicant_address = applicant_address
    g.session.commit()

    return redirect(ReviewRouter.get_redirect_url('add_lon.get_dominant_building_info'))
