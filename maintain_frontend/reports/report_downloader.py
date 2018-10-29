from flask import current_app, request, render_template, redirect
from maintain_frontend.exceptions import ApplicationError, ExpiredReportValidationError
from maintain_frontend.dependencies.storage_api.storage_api_service import StorageAPIService
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from flask import Blueprint, g
import jwt


reports_bp = Blueprint('reports', __name__,
                       static_url_path='/static/reports',
                       static_folder='static',
                       template_folder='templates')


@reports_bp.route('/expired-charges-report')
@requires_permission([Permissions.view_report])
def get_expired_charges_report():
    current_app.logger.info('Validating token for report download')
    token = request.args.get('token')

    if token is None:
        current_app.logger.error('No token provided')
        return redirect('/not-authorised')

    try:
        report_info = validate_token(token)
    except ExpiredReportValidationError:
        current_app.logger.error('Invalid token')
        return redirect('/not-authorised')
    except Exception as ex:
        error_message = "Failed to validate expired report token - {}".format(ex)
        current_app.logger.error(error_message)
        raise ApplicationError(500)

    current_app.logger.info('Token validated, getting external URL for report')
    storage_api_service = StorageAPIService(current_app.config)

    report_url = storage_api_service.get_external_url(report_info['report_id'],
                                                      current_app.config['EXPIRED_REPORT_BUCKET'])

    if report_url is None:
        current_app.logger.error('No URL returned for report from storage-api')
        raise ApplicationError(404)

    return render_template('expired_charges_report_download.html', report_url=report_url)


def validate_token(token):

    try:
        report_info = jwt.decode(token, current_app.config['EXPIRED_REPORT_KEY'], algorithm='HS256')
    except jwt.InvalidTokenError as ex:
        current_app.logger.error('Can not validate json web token - {}'.format(ex))
        raise ExpiredReportValidationError("Invalid token")
    except Exception as ex:
        current_app.logger.error('Can not validate json web token - {}'.format(ex))
        raise ExpiredReportValidationError("Error reading token")

    if 'report_id' not in report_info or 'authority' not in report_info:
        current_app.logger.error('Expected fields not found in token')
        raise ExpiredReportValidationError('Expected fields not found in token')

    if g.session.user.organisation != 'HM Land Registry' and g.session.user.organisation != report_info['authority']:
        error_message = "Requesting user does not belong to correct authority for this report. " \
                        "User authority: '{}', Report authority: '{}'" \
            .format(g.session.user.organisation, report_info['authority'])
        current_app.logger.error(error_message)
        raise ExpiredReportValidationError('Expected fields not found in token')

    return report_info
