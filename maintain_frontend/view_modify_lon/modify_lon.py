from flask import g, current_app, render_template, url_for, redirect, request
from maintain_frontend.dependencies.storage_api.storage_api_service import StorageAPIService
from maintain_frontend.dependencies.search_api.local_land_charge_service import LocalLandChargeService
from maintain_frontend.services.charge_id_services import calc_display_id
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.services.charge_services import get_lon_by_charge_id
from maintain_frontend.view_modify_lon.validation.vary_lon_validator import VaryLonValidator
from maintain_frontend.add_lon.services import process_lon_documents
from maintain_frontend.exceptions import UploadDocumentError, ApplicationError
from dateutil.relativedelta import relativedelta
import datetime


def register_routes(bp):
    bp.add_url_rule('/<charge_id>', view_func=modify_lon_upload_get, methods=['GET'])
    bp.add_url_rule('/<charge_id>', view_func=modify_lon_upload_post, methods=['POST'])


@requires_permission([Permissions.vary_lon])
def modify_lon_upload_get(charge_id):
    current_app.logger.info("Endpoint called with charge_id='{}'".format(charge_id))
    local_land_charge_service = LocalLandChargeService(current_app.config)

    # Retrieve Light Obstruction Notice Item
    display_id, charge_item = get_lon_by_charge_id(charge_id, local_land_charge_service)
    g.session.edited_fields = {}
    g.session.commit()

    # Check that charge hasn't been cancelled in case user attempts to navigate to update URL manually
    if charge_item.end_date:
        current_app.logger.error('Attempted to update a cancelled charge.  Charge ID: {}'.format(charge_id))
        raise ApplicationError(500)

    # If the charge is in session we are in the process of updating it
    if not g.session.add_lon_charge_state:
        g.session.add_lon_charge_state = charge_item
        g.session.commit()

        current_app.logger.info("Session charge updated - Rendering Template")
        return render_template('modify_lon_upload.html', charge_id=display_id, charge_item=charge_item)

    else:
        session_charge_id = calc_display_id(g.session.add_lon_charge_state.local_land_charge)

        # Check that charge ID in session and URL match.
        # If they don't, redirect user to the charge ID they entered and clear session
        if session_charge_id != display_id:
            g.session.add_lon_charge_state = None
            g.session.commit()
            return redirect(url_for("modify_lon.modify_lon_upload_get", charge_id=charge_id))

        return render_template('modify_lon_upload.html', charge_id=display_id, charge_item=charge_item)


@requires_permission([Permissions.vary_lon])
def modify_lon_upload_post(charge_id):
    # Retrieve Charge
    local_land_charge_service = LocalLandChargeService(current_app.config)
    display_id, charge_item = get_lon_by_charge_id(charge_id, local_land_charge_service)

    validation_error_builder = VaryLonValidator.validate(request.form, request.files)

    if validation_error_builder.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template('modify_lon_upload.html',
                               charge_id=display_id,
                               charge_item=charge_item,
                               validation_errors=validation_error_builder.errors,
                               validation_summary_heading=validation_error_builder.summary_heading_text,
                               request_body=request.form), 400

    handle_vary_lon_options_choice(charge_id, charge_item)
    return redirect(url_for('modify_lon.modify_lon_details_get', charge_id=charge_id))


def handle_vary_lon_options_choice(charge_id, charge_item):
    vary_lon_options = request.form.getlist('vary-lon-options')
    definitive_certificate = request.files.get('definitive-certificate-file-input')
    form_b = request.files.get('form-b-file-input')
    court_order = request.files.get('court-order-file-input')

    files_to_upload = {}

    if "Definitive Certificate" in vary_lon_options and definitive_certificate:
        tribunal_definitive_certificate_date = datetime.date(
            int(request.form.get('definitive_cert_year')),
            int(request.form.get('definitive_cert_month')),
            int(request.form.get('definitive_cert_day'))
        )

        if tribunal_definitive_certificate_date:
            current_app.logger.info("Update tribunal_definitive_certificate_date and expiry_date in session object")
            charge_item.tribunal_definitive_certificate_date = tribunal_definitive_certificate_date
            charge_item.expiry_date = datetime.date.today() + relativedelta(years=+21)
            g.session.edited_fields['tribunal-definitive-certificate-date'] = "Tribunal definitive certificate date"
            g.session.edited_fields['expiry-date'] = "Expiry date"

        g.session.edited_fields['definitive-certificate'] = "Definitive Certificate"
        files_to_upload['definitive-certificate'] = ('definitive_certificate.pdf', definitive_certificate,
                                                     definitive_certificate.content_type)

    if "Form B" in vary_lon_options and form_b:
        files_to_upload['form-b'] = ('form_b.pdf', form_b, form_b.content_type)

    if "Court Order" in vary_lon_options and court_order:
        files_to_upload['court-order'] = ("court_order.pdf", court_order, court_order.content_type)

    if files_to_upload:
        upload_files(files_to_upload, charge_item, charge_id)


def upload_files(files, charge_item, charge_id):
    storage_api_service = StorageAPIService(current_app.config)
    subdirectory = charge_item.documents_filed['form-a'][0]['subdirectory']

    upload_response = storage_api_service.save_files(files, process_lon_documents.bucket(),
                                                     [subdirectory], True)

    if upload_response.status_code == 400:
        raise UploadDocumentError("Virus scan failed. Upload a new document.",
                                  url_for('modify_lon.modify_lon_upload_get', charge_id=charge_id))

    new_documents_filed = upload_response.json()

    merged_docs = charge_item.documents_filed.copy()
    merged_docs.update(new_documents_filed)

    charge_item.documents_filed = merged_docs

    g.session.add_lon_charge_state = charge_item
    g.session.commit()
