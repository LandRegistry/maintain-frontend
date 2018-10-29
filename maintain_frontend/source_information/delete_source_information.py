from flask import render_template, current_app, g, redirect, url_for, request

from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.decorators import requires_permission
from maintain_frontend.dependencies.local_authority_api.local_authority_api_service import LocalAuthorityService


def register_routes(bp):
    bp.add_url_rule('/source-information/delete', view_func=get_delete_source_information, methods=['GET'])
    bp.add_url_rule('/source-information/delete', view_func=post_delete_source_information, methods=['POST'])
    bp.add_url_rule('/source-information/delete/success', view_func=get_delete_source_information_success,
                    methods=['GET'])


@requires_permission([Permissions.manage_source_information])
def get_delete_source_information():
    current_app.logger.info("Delete source information page requested")

    if g.session.source_information is None or g.session.source_information_id is None:
        return redirect(url_for('source_info.get_source_information'))

    return render_template('delete-source-information-confirm.html', source_information=g.session.source_information)


@requires_permission([Permissions.manage_source_information])
def post_delete_source_information():
    if g.session.source_information_id is None:
        return redirect(url_for('source_info.get_source_information'))

    submit_token = request.form.get('csrf_token')
    local_authority_service = LocalAuthorityService(current_app.config)

    if submit_token != g.session.submit_token:
        g.session.submit_token = submit_token
        g.session.commit()
        local_authority_service.delete_source_information_for_organisation(g.session.user.organisation,
                                                                           g.session.source_information_id)

    return redirect(url_for('source_info.get_delete_source_information_success'))


@requires_permission([Permissions.manage_source_information])
def get_delete_source_information_success():
    current_app.logger.info("Update source information success page requested")

    g.session.source_information = None
    g.session.source_information_id = None
    g.session.commit()
    return render_template('source-information-operation-success.html',
                           success_message="Source information deleted successfully")
