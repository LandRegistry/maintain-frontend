from flask import render_template, current_app, g, request, redirect, url_for

from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.decorators import requires_permission, requires_two_factor_authentication
from maintain_frontend.dependencies.local_authority_api.local_authority_api_service import LocalAuthorityService


def register_routes(bp):
    bp.add_url_rule('/source-information', view_func=get_source_information, methods=['GET'])
    bp.add_url_rule('/source-information', view_func=post_source_information, methods=['POST'])


@requires_permission([Permissions.manage_source_information])
@requires_two_factor_authentication()
def get_source_information():
    current_app.logger.info("Source information page requested")
    g.session.source_information = None
    g.session.source_information_id = None
    g.session.commit()

    local_authority_service = LocalAuthorityService(current_app.config)
    source_information_list = local_authority_service.get_source_information_for_organisation(
        g.session.user.organisation)

    return render_template('source-information.html', source_information_list=source_information_list)


@requires_permission([Permissions.manage_source_information])
@requires_two_factor_authentication()
def post_source_information():
    current_app.logger.info("Post Source information page requested")

    source_info_operation = request.form.get('submit')

    g.session.source_information_id = request.form.get('source-information-id')
    g.session.source_information = request.form.get('source-information')
    g.session.commit()

    if source_info_operation == 'Update':
        return redirect(url_for('source_info.get_update_source_information'))
    elif source_info_operation == 'Delete':
        return redirect(url_for('source_info.get_delete_source_information'))

    return redirect(url_for('source_info.get_source_information'))
