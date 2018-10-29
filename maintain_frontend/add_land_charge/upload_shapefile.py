import json
import fiona
import datetime
from flask import g, redirect, url_for, render_template, current_app, request
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.add_land_charge.validation.upload_shapefile_validator import UploadShapefileValidator


def register_routes(bp):
    bp.add_url_rule('/add-local-land-charge/upload-shapefile', view_func=get_upload_shapefile, methods=['GET'])
    bp.add_url_rule('/add-local-land-charge/upload-shapefile', view_func=post_upload_shapefile, methods=['POST'])
    bp.add_url_rule('/add-local-land-charge/save-existing-geometries-and-upload',
                    view_func=post_save_existing_geometries, methods=['POST'])


@requires_permission([Permissions.add_llc])
def get_upload_shapefile():
    current_app.logger.info('Endpoint called')

    if g.session.add_charge_state is None:
        current_app.logger.info('Redirecting to: {}'.format(url_for('add_land_charge.new')))
        return redirect(url_for('add_land_charge.new'))

    g.session.upload_shapefile_processed = None
    g.session.commit()

    return render_template("upload_shapefile.html")


@requires_permission([Permissions.add_llc])
def post_upload_shapefile():
    current_app.logger.info('Endpoint called')

    if g.session.add_charge_state is None:
        current_app.logger.info('Redirecting to: {}'.format(url_for('add_land_charge.new')))
        return redirect(url_for('add_land_charge.new'))

    file = request.files.get('shapefile-input')
    submit_token = request.form.get('csrf_token')
    unique_request = submit_token != g.session.submit_token
    already_uploaded = (not unique_request) and g.session.upload_shapefile_processed

    validation_errors = UploadShapefileValidator.validate(file, g.session.add_charge_state.geometry,
                                                          already_uploaded)

    if validation_errors.errors:
        current_app.logger.error('Validation errors when uploading shapefile')
        return render_template("upload_shapefile.html",
                               validation_errors=validation_errors.errors,
                               validation_summary_heading=validation_errors.summary_heading_text)

    if unique_request and not already_uploaded:
        g.session.submit_token = submit_token
        g.session.commit()

        geometries = parse_upload(file)

        if g.session.add_charge_state.geometry:
            g.session.add_charge_state.geometry['features'].extend(geometries)
        else:
            g.session.add_charge_state.geometry = {
                "type": "FeatureCollection",
                "features": geometries
            }
        g.session.upload_shapefile_processed = True
        g.session.commit()

    return redirect(url_for('add_land_charge.get_location', upload=True))


@requires_permission([Permissions.add_llc])
def post_save_existing_geometries():
    if request.form.get('saved-features-upload'):
        information = json.loads(request.form['saved-features-upload'].strip())
        g.session.add_charge_state.geometry = information
    else:
        g.session.add_charge_state.geometry = None
    g.session.commit()

    return redirect(url_for('add_land_charge.get_upload_shapefile'))


def parse_upload(uploaded_file):
    geometries = []

    with fiona.drivers():
        with fiona.BytesCollection(uploaded_file.read()) as shpfile:
            count = 0
            current_timestamp = int(datetime.datetime.now().timestamp() * 1000)
            for shape in shpfile:
                geometry_id = current_timestamp + count
                shape_obj = {
                    'geometry': shape['geometry'],
                    'type': 'Feature',
                    'properties': {
                        'id': geometry_id
                    }
                }
                geometries.append(shape_obj)
                count += 1

    return geometries
