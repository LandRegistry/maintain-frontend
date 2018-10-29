from flask import render_template, current_app, request, redirect, url_for, g

from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.decorators import requires_permission
from maintain_frontend.source_information.validation.source_information_validator import SourceInformationValidator
from maintain_frontend.dependencies.local_authority_api.local_authority_api_service import LocalAuthorityService


def register_routes(bp):
    bp.add_url_rule('/source-information/update', view_func=get_update_source_information, methods=['GET'])
    bp.add_url_rule('/source-information/update', view_func=post_update_source_information, methods=['POST'])
    bp.add_url_rule('/source-information/update/success', view_func=get_update_source_information_success,
                    methods=['GET'])


@requires_permission([Permissions.manage_source_information])
def get_update_source_information():
    current_app.logger.info("Update Source information page requested")

    if g.session.source_information is None or g.session.source_information_id is None:
        return redirect(url_for('source_info.get_source_information'))

    return render_template('update-source-information.html', source_information=g.session.source_information)


@requires_permission([Permissions.manage_source_information])
def post_update_source_information():
    current_app.logger.info("Post Update Source information page requested")

    if g.session.source_information is None or g.session.source_information_id is None:
        return redirect(url_for('source_info.get_source_information'))

    source_info = request.form['source-information'].strip()

    current_app.logger.info("Running validation")
    validation_errors = SourceInformationValidator.validate(source_info)

    if validation_errors.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template('update-source-information.html',
                               source_information=source_info,
                               validation_errors=validation_errors.errors,
                               validation_summary_heading=validation_errors.summary_heading_text), 400

    submit_token = request.form.get('csrf_token')
    local_authority_service = LocalAuthorityService(current_app.config)

    if submit_token != g.session.submit_token:
        g.session.submit_token = submit_token
        g.session.source_information = source_info
        g.session.commit()

        local_authority_service.update_source_information_for_organisation(
            g.session.source_information_id,
            g.session.source_information,
            g.session.user.organisation)

    return redirect(url_for('source_info.get_update_source_information_success'))


@requires_permission([Permissions.manage_source_information])
def get_update_source_information_success():
    current_app.logger.info("Update source information success page requested")

    g.session.source_information = None
    g.session.source_information_id = None
    g.session.commit()
    return render_template('source-information-operation-success.html',
                           success_message="Source information updated successfully")
