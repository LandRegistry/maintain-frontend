from flask import render_template, request, current_app, g, redirect, url_for
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.view_modify_lon.validation.cancel_lon_validator import CancelLonValidator
from maintain_frontend.dependencies.storage_api.storage_api_service import StorageAPIService
from maintain_frontend.add_lon.services import process_lon_documents
from maintain_frontend.dependencies.audit_api.audit_api import AuditAPIService
from maintain_frontend.dependencies.maintain_api.maintain_api_service import MaintainApiService
from maintain_frontend.dependencies.search_api.local_land_charge_service import LocalLandChargeService
from maintain_frontend.exceptions import UploadDocumentError
from maintain_frontend.services.charge_services import get_lon_by_charge_id
from datetime import date
import json


def register_routes(bp):
    bp.add_url_rule('/<charge_id>', view_func=cancel_get, methods=['GET'])
    bp.add_url_rule('/<charge_id>', view_func=cancel_post, methods=['POST'])
    bp.add_url_rule('/<charge_id>/confirmation', view_func=confirm, methods=['GET', 'POST'])
    bp.add_url_rule('/<charge_id>/charge-cancelled', view_func=charge_cancelled, methods=['GET'])


# Cancel LON start Page
@requires_permission([Permissions.cancel_lon])
def cancel_get(charge_id):
    # Retrieve Charge
    local_land_charge_service = LocalLandChargeService(current_app.config)
    display_id, charge_item = get_lon_by_charge_id(charge_id, local_land_charge_service)
    return render_template('cancel_lon.html', charge_id=display_id)


# Cancel LON start Page
@requires_permission([Permissions.cancel_lon])
def cancel_post(charge_id):
    local_land_charge_service = LocalLandChargeService(current_app.config)
    display_id, charge_item = get_lon_by_charge_id(charge_id, local_land_charge_service)

    cancel_options = request.form.getlist('cancel-options')
    form_b = request.files.get('form-b-cancel-lon-file-input')
    court_order = request.files.get('court-order-cancel-lon-file-input')

    current_app.logger.info("Running validation")
    validation_error_builder = CancelLonValidator.validate(request.form, request.files)

    if validation_error_builder.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template('cancel_lon.html',
                               charge_id=display_id,
                               validation_errors=validation_error_builder.errors,
                               validation_summary_heading=validation_error_builder.summary_heading_text,
                               request_body=request.form), 400

    files_to_upload = {}

    if "Form B" in cancel_options and form_b:
        files_to_upload['form-b'] = ('form_b.pdf', form_b, form_b.content_type)

    if "Court Order" in cancel_options and court_order:
        files_to_upload['court-order'] = ("court_order.pdf", court_order, court_order.content_type)

    if files_to_upload:
        upload_files(files_to_upload, charge_item, charge_id)

    charge_item.end_date = date.today()

    g.session.add_lon_charge_state = charge_item
    g.session.commit()

    return redirect(url_for('cancel_lon.confirm', charge_id=charge_id))


def upload_files(files, charge_item, charge_id):
    storage_api_service = StorageAPIService(current_app.config)
    subdirectory = charge_item.documents_filed['form-a'][0]['subdirectory']

    upload_response = storage_api_service.save_files(files, process_lon_documents.bucket(),
                                                     [subdirectory], True)

    if upload_response.status_code == 400:
        raise UploadDocumentError("Virus scan failed. Upload a new document.",
                                  url_for('cancel_lon.cancel_get', charge_id=charge_id))

    new_documents_filed = upload_response.json()

    merged_docs = charge_item.documents_filed.copy()
    merged_docs.update(new_documents_filed)

    charge_item.documents_filed = merged_docs


# Cancel LON start Page
@requires_permission([Permissions.cancel_lon])
def confirm(charge_id):
    local_land_charge_service = LocalLandChargeService(current_app.config)
    display_id, charge_item = get_lon_by_charge_id(charge_id, local_land_charge_service)

    if request.method == 'GET':
        return render_template('cancel_lon_confirm.html',
                               charge_id=display_id,
                               charge_item=charge_item,
                               geometry=json.dumps(charge_item.geometry))
    if request.method == 'POST':
        current_app.logger.info("Cancelling Charge - {}".format(display_id))
        AuditAPIService.audit_event("Cancelling charge", supporting_info={'id': display_id})
        MaintainApiService.update_charge(g.session.add_lon_charge_state)
        # This is required because if the render_template is called from this post method then the flow won't be able
        # to return to the confirmation page if the user goes to the feedback form from the confirmation page
        return redirect(url_for('cancel_lon.charge_cancelled', charge_id=display_id))


# Cancel LON confirmed Page
@requires_permission([Permissions.cancel_lon])
def charge_cancelled(charge_id):
    return render_template('charge_cancelled.html', charge_id=charge_id)
