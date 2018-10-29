from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.dependencies.audit_api.audit_api import AuditAPIService
from maintain_frontend.dependencies.llc1_document_api.llc1_document_api import LLC1DocumentService
from maintain_frontend.dependencies.report_api.report_api_service import ReportAPIService
from flask import current_app, g, url_for, redirect, render_template
from datetime import datetime, timezone


def register_routes(bp):
    bp.add_url_rule('/create-official-search/download-result', view_func=llc1_get_result, methods=['GET'])


@requires_permission([Permissions.request_llc1])
def llc1_get_result():
    current_app.logger.info('Endpoint called')
    if g.session.llc1_state is None:
        current_app.logger.info('Redirecting to: %s', url_for("create_llc1.create_llc1"))
        return redirect(url_for("create_llc1.create_llc1"))

    current_app.logger.info("Calling LLC1 Document API")
    AuditAPIService.audit_event("User submitted an LLC Official Search request")
    document_service = LLC1DocumentService(current_app.config)
    response = document_service.generate(g.session.llc1_state.description, g.session.llc1_state.extent)

    ReportAPIService.send_number_of_charges_per_search_data({
        'date': datetime.now(timezone.utc).isoformat(),
        'channel': 'MAINTAIN',
        'number_of_charges': response['number_of_charges'],
        # TODO(): Update once repeat searches are added to the Maintain service to check if
        # this is a repeat search
        'repeat': False
    })

    current_app.logger.info("Adding LLC1 URL to session state")
    g.session.llc1_state.llc1_url = response['document_url']
    g.session.llc1_state.external_llc1_url = response['external_url']
    g.session.commit()

    current_app.logger.info("Render template 'search_result.html'")
    return render_template('search_result.html',
                           url=g.session.llc1_state.external_llc1_url,
                           supporting_documents=response.get('supporting_documents'))
