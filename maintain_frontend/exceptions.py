from flask import current_app, redirect, url_for, render_template
from flask_wtf.csrf import CSRFError


class ApplicationError(Exception):
    """This class is to be raised when the client should be informed of a problem.

    Example:
        raise ApplicationError(400)

    The handler method will then create an error with the appropriate information.
    """
    def __init__(self, http_code=500):
        Exception.__init__(self)
        self.http_code = http_code


class UploadDocumentError(Exception):
    """This class is to be raised when the client should be informed of a problem when uploading documents

    Example:
        raise UploadDocumentError("Virus Scan Failed", url_for('add_lon.get_upload_lon_documents'))

    The handler method will then create an error with the appropriate information.
    """
    def __init__(self, message, redirect_url):
        Exception.__init__(self)
        self.status_code = 400
        self.message = message
        self.redirect_url = redirect_url


class ExpiredReportValidationError(Exception):
    """This class is to be raised when failing to validate expired report tokens.

    Example:
        raise ExpiredReportValidationError("Invalid token")

    The handler method will then create an error with the appropriate information.
    """
    def __init__(self, message):
        Exception.__init__(self)
        self.status_code = 403
        self.message = message


def unhandled_exception(e):
    current_app.logger.exception('Unhandled Exception: %s', repr(e))
    return redirect('/error')


def application_error(e):
    current_app.logger.debug('Application Exception: %s', repr(e), exc_info=True)

    if e.http_code == 404:
        return redirect('/page-not-found')
    else:
        return redirect('/error')


def register_exception_handlers(app):
    app.register_error_handler(ApplicationError, application_error)
    app.register_error_handler(Exception, unhandled_exception)

    @app.errorhandler(404)
    def page_not_found(e):
        return redirect('/page-not-found')

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        current_app.logger.warning('CSRF protection reports an error: %s', repr(e))
        return redirect(url_for('exception_handler.error'))

    @app.errorhandler(UploadDocumentError)
    def handle_upload_document_error(e):
        current_app.logger.warning('Upload document error: %s', repr(e))
        return render_template('error/upload_document_error.html', error=e)

    app.logger.info("Exception handlers registered")
