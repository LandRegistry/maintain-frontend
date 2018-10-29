from flask import current_app, render_template, url_for, redirect, g
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.services.charge_services import get_history_update_info_by_charge_id, get_lon_by_charge_id
from maintain_frontend.constants.lon_defaults import LonDefaults
from maintain_frontend.dependencies.audit_api.audit_api import AuditAPIService
from maintain_frontend.dependencies.search_api.local_land_charge_service import LocalLandChargeService
from maintain_frontend.dependencies.storage_api.storage_api_service import StorageAPIService
import json


def register_routes(bp):
    bp.add_url_rule('/<charge_id>', view_func=view_lon, methods=['GET'])


@requires_permission([Permissions.retrieve_llc])
def view_lon(charge_id):
    current_app.logger.info("Endpoint called - Clearing session charge")

    local_land_charge_service = LocalLandChargeService(current_app.config)

    # Clear these session values if someone quit an edit back to the view page
    g.session.add_lon_charge_state = None
    g.session.edited_fields = None
    g.session.commit()
    current_app.logger.info("Charge cleared from session")

    display_id, charge_item = get_lon_by_charge_id(charge_id, local_land_charge_service)
    # Let the LLC blueprint handle LLC's
    if charge_item.charge_type != LonDefaults.charge_type:
        return redirect(url_for('view_land_charge.view_land_charge', local_land_charge=charge_id))

    updated, updated_date = get_history_update_info_by_charge_id(charge_id, local_land_charge_service)

    AuditAPIService.audit_event("User viewing LON: {}".format(charge_id))

    return render_template('view_lon.html', charge_id=display_id, charge_item=charge_item,
                           updated=updated, updated_date=updated_date, geometry=json.dumps(charge_item.geometry),
                           document_urls=get_external_url_for_docs(charge_item))


def get_external_url_for_docs(charge_item):
    service = StorageAPIService(current_app.config)
    document_urls = {}
    append_urls_for_doc(service, 'temporary-certificate', charge_item.documents_filed, document_urls)
    append_urls_for_doc(service, 'definitive-certificate', charge_item.documents_filed, document_urls)
    append_urls_for_doc(service, 'form-a', charge_item.documents_filed, document_urls)
    append_urls_for_doc(service, 'form-b', charge_item.documents_filed, document_urls)
    append_urls_for_doc(service, 'court-order', charge_item.documents_filed, document_urls)

    return document_urls


def append_urls_for_doc(storage_api_service, doc_name, docs, doc_urls):
    if doc_name in docs and docs[doc_name]:
        doc_urls[doc_name] = []
        for doc in docs[doc_name]:
            url = storage_api_service.get_external_url_from_path(doc['reference'])
            doc_urls[doc_name].append(url)
