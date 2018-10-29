import datetime

from flask import g, render_template, redirect, url_for, current_app, request

from maintain_frontend.add_lon.validation.upload_lon_documents_validator import UploadLonDocumentsValidator
from maintain_frontend.add_lon.services import process_lon_documents
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.decorators import requires_permission
from maintain_frontend.dependencies.storage_api.storage_api_service import StorageAPIService
from maintain_frontend.exceptions import UploadDocumentError
from dateutil.relativedelta import relativedelta
from maintain_frontend.add_lon.routing.review_router import ReviewRouter

from werkzeug.datastructures import MultiDict


def register_routes(bp):
    bp.add_url_rule('/add-light-obstruction-notice/upload-light-obstruction-notice-documents',
                    view_func=get_upload_lon_documents, methods=['GET'])
    bp.add_url_rule('/add-light-obstruction-notice/upload-light-obstruction-notice-documents',
                    view_func=post_upload_lon_documents, methods=['POST'])


@requires_permission([Permissions.add_lon])
def get_upload_lon_documents():
    if g.session.add_lon_charge_state is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_lon.new"))
        return redirect(url_for("add_lon.new"))

    request_body = MultiDict()

    if g.session.add_lon_charge_state.tribunal_temporary_certificate_date:
        request_body.add('certificate', 'Temporary LON certificate')

        request_body.add('temp_cert_year', g.session.add_lon_charge_state.tribunal_temporary_certificate_date.year)
        request_body.add('temp_cert_month', g.session.add_lon_charge_state.tribunal_temporary_certificate_date.month)
        request_body.add('temp_cert_day', g.session.add_lon_charge_state.tribunal_temporary_certificate_date.day)

        request_body.add('temp_expiry_year',
                         g.session.add_lon_charge_state.tribunal_temporary_certificate_expiry_date.year)
        request_body.add('temp_expiry_month',
                         g.session.add_lon_charge_state.tribunal_temporary_certificate_expiry_date.month)
        request_body.add('temp_expiry_day',
                         g.session.add_lon_charge_state.tribunal_temporary_certificate_expiry_date.day)

    if g.session.add_lon_charge_state.tribunal_definitive_certificate_date:
        request_body.add('certificate', 'Definitive LON certificate')

        request_body.add('definitive_cert_year',
                         g.session.add_lon_charge_state.tribunal_definitive_certificate_date.year)
        request_body.add('definitive_cert_month',
                         g.session.add_lon_charge_state.tribunal_definitive_certificate_date.month)
        request_body.add('definitive_cert_day',
                         g.session.add_lon_charge_state.tribunal_definitive_certificate_date.day)

    current_app.logger.info("Displaying page 'upload_lon_documents.html'")
    return render_template('upload_lon_documents.html',
                           request_body=request_body)


@requires_permission([Permissions.add_lon])
def post_upload_lon_documents():
    upload_lon_documents_form = request.form

    current_app.logger.info("Running validation")
    validation_error_builder = UploadLonDocumentsValidator.validate(upload_lon_documents_form, request.files)

    if validation_error_builder.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template('upload_lon_documents.html',
                               validation_errors=validation_error_builder.errors,
                               validation_summary_heading=validation_error_builder.summary_heading_text,
                               request_body=request.form), 400

    current_app.logger.info("Updating session object")
    update_lon_document_fields(upload_lon_documents_form)
    upload_response = upload_lon_docs(request.files, upload_lon_documents_form)

    if upload_response.status_code == 400:
        raise UploadDocumentError("Virus scan failed. Upload a new document.",
                                  url_for('add_lon.get_upload_lon_documents'))

    filenames = {"form_a": request.files.get('form-a-file-input').filename}

    if "Temporary LON certificate" in upload_lon_documents_form.getlist('certificate'):
        filenames["temporary_lon_cert"] = request.files.get('temporary-lon-cert-file-input').filename
    else:
        filenames["temporary_lon_cert"] = ''

    if "Definitive LON certificate" in upload_lon_documents_form.getlist('certificate'):
        filenames["definitive_lon_cert"] = request.files.get('definitive-lon-cert-file-input').filename
    else:
        filenames["definitive_lon_cert"] = ''

    ReviewRouter.update_edited_filename_field(filenames)

    g.session.filenames = filenames
    g.session.add_lon_charge_state.documents_filed = upload_response.json()
    g.session.commit()

    current_app.logger.info("Redirecting to: %s", url_for("add_lon.get_servient_structure_height"))
    return redirect(ReviewRouter.get_redirect_url('add_lon.get_servient_structure_height'))


def update_lon_document_fields(upload_lon_documents_form):
    definitive_cert = "Definitive LON certificate"
    temporary_cert = "Temporary LON certificate"

    if definitive_cert in upload_lon_documents_form.getlist('certificate'):
        tribunal_definitive_certificate_date = datetime.date(
            int(upload_lon_documents_form.get('definitive_cert_year')),
            int(upload_lon_documents_form.get('definitive_cert_month')),
            int(upload_lon_documents_form.get('definitive_cert_day'))
        )

        if tribunal_definitive_certificate_date:
            current_app.logger.info("Update tribunal_definitive_certificate_date in session object")
            ReviewRouter.update_edited_field('tribunal_definitive_certificate_date',
                                             tribunal_definitive_certificate_date)
            g.session.add_lon_charge_state.tribunal_definitive_certificate_date = tribunal_definitive_certificate_date
            g.session.add_lon_charge_state.expiry_date = datetime.date.today() + relativedelta(years=+21)
    else:
        # Need this in case they are coming from review page and are removing an existing date by un-checking box
        ReviewRouter.remove_from_edited_fields('tribunal_definitive_certificate_date')
        g.session.add_lon_charge_state.tribunal_definitive_certificate_date = None
        g.session.add_lon_charge_state.expiry_date = None

    if temporary_cert in upload_lon_documents_form.getlist('certificate'):
        tribunal_temporary_certificate_date = datetime.date(
            int(upload_lon_documents_form.get('temp_cert_year')),
            int(upload_lon_documents_form.get('temp_cert_month')),
            int(upload_lon_documents_form.get('temp_cert_day'))
        )

        if tribunal_temporary_certificate_date:
            current_app.logger.info("Update tribunal_temporary_certificate_date in session object")
            ReviewRouter.update_edited_field('tribunal_temporary_certificate_date',
                                             tribunal_temporary_certificate_date)
            g.session.add_lon_charge_state.tribunal_temporary_certificate_date = tribunal_temporary_certificate_date

        tribunal_temporary_certificate_expiry_date = datetime.date(
            int(upload_lon_documents_form.get('temp_expiry_year')),
            int(upload_lon_documents_form.get('temp_expiry_month')),
            int(upload_lon_documents_form.get('temp_expiry_day'))
        )

        if tribunal_temporary_certificate_expiry_date:
            current_app.logger.info("Update tribunal_temporary_certificate_expiry_date in session object")
            ReviewRouter.update_edited_field('tribunal_temporary_certificate_expiry_date',
                                             tribunal_temporary_certificate_expiry_date)
            g.session.add_lon_charge_state.tribunal_temporary_certificate_expiry_date = \
                tribunal_temporary_certificate_expiry_date

    else:
        # Need this in case they are coming from review page and are removing an existing date by un-checking box
        ReviewRouter.remove_from_edited_fields('tribunal_temporary_certificate_date')
        ReviewRouter.remove_from_edited_fields('tribunal_temporary_certificate_expiry_date')
        g.session.add_lon_charge_state.tribunal_temporary_certificate_date = None
        g.session.add_lon_charge_state.tribunal_temporary_certificate_expiry_date = None


def upload_lon_docs(files, upload_lon_documents_form):
    storage_api_service = StorageAPIService(current_app.config)

    form_a = files.get('form-a-file-input')
    files_to_upload = {'form-a': ('form_a.pdf', form_a, form_a.content_type)}

    if "Definitive LON certificate" in upload_lon_documents_form.getlist('certificate'):
        # Need this check in case they have un-selected the "definitive" checkbox but there is still data in the
        # definitive file field. So only do this upload if the checkbox is selected.
        definitive_certificate = files.get('definitive-lon-cert-file-input')
        if definitive_certificate:
            files_to_upload['definitive-certificate'] = ('definitive_certificate.pdf', definitive_certificate,
                                                         definitive_certificate.content_type)

    if "Temporary LON certificate" in upload_lon_documents_form.getlist('certificate'):
        # Need this check in case they have un-selected the "temporary" checkbox but there is still data in the
        # temporary file field. So only do this upload if the checkbox is selected.
        temporary_certificate = files.get('temporary-lon-cert-file-input')
        if temporary_certificate:
            files_to_upload['temporary-certificate'] = ("temporary_certificate.pdf",
                                                        temporary_certificate, temporary_certificate.content_type)

    return storage_api_service.save_files(files_to_upload,
                                          process_lon_documents.bucket(),
                                          [process_lon_documents.generate_uuid()],
                                          True)
