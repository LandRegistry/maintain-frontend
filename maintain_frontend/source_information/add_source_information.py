from flask import render_template, current_app, request, redirect, url_for, g

from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.decorators import requires_permission
from maintain_frontend.source_information.validation.source_information_validator import SourceInformationValidator
from maintain_frontend.dependencies.local_authority_api.local_authority_api_service import LocalAuthorityService


def register_routes(bp):
    bp.add_url_rule('/source-information/add', view_func=get_add_source_information, methods=['GET'])
    bp.add_url_rule('/source-information/add', view_func=post_add_source_information, methods=['POST'])
    bp.add_url_rule('/source-information/add/confirm', view_func=get_add_source_information_confirm, methods=['GET'])
    bp.add_url_rule('/source-information/add/confirm', view_func=post_add_source_information_confirm, methods=['POST'])
    bp.add_url_rule('/source-information/add/success', view_func=get_add_source_information_success, methods=['GET'])


@requires_permission([Permissions.manage_source_information])
def get_add_source_information():
    current_app.logger.info("Add Source information page requested")

    return render_template('add-source-information.html', source_information=g.session.source_information)


@requires_permission([Permissions.manage_source_information])
def post_add_source_information():
    source_info = request.form['source-information'].strip()

    current_app.logger.info("Running validation")
    validation_errors = SourceInformationValidator.validate(source_info)

    if validation_errors.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template('add-source-information.html',
                               validation_errors=validation_errors.errors,
                               validation_summary_heading=validation_errors.summary_heading_text,
                               source_information=source_info), 400

    g.session.source_information = source_info
    g.session.commit()

    return redirect(url_for('source_info.get_add_source_information_confirm'))


@requires_permission([Permissions.manage_source_information])
def get_add_source_information_confirm():
    current_app.logger.info("Confirm add source information page requested")

    if g.session.source_information is None:
        return redirect(url_for('source_info.get_add_source_information'))

    return render_template('add-source-information-confirm.html', source_information=g.session.source_information)


@requires_permission([Permissions.manage_source_information])
def post_add_source_information_confirm():
    if g.session.source_information is None:
        return redirect(url_for('source_info.get_add_source_information'))

    submit_token = request.form.get('csrf_token')
    local_authority_service = LocalAuthorityService(current_app.config)

    if submit_token != g.session.submit_token:
        g.session.submit_token = submit_token
        g.session.commit()
        local_authority_service.add_source_information_for_organisation(g.session.source_information,
                                                                        g.session.user.organisation)
    return redirect(url_for('source_info.get_add_source_information_success'))


@requires_permission([Permissions.manage_source_information])
def get_add_source_information_success():
    current_app.logger.info("Add source information success page requested")

    g.session.source_information = None
    g.session.commit()
    return render_template('source-information-operation-success.html',
                           success_message="Source information added successfully")
