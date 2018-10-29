from flask_logconfig import LogConfig
import logging
import json
import traceback
from flask import g, ctx, request
from flask_wtf import CSRFProtect
import collections

# Create empty extension objects here
logger = LogConfig()
csrf = CSRFProtect()


def register_extensions(app):
    """Adds any previously created extension objects into the app, and does any further setup they need."""
    # Logging
    logger.init_app(app)

    # CSRF protection
    csrf.init_app(app)

    # All done!
    app.logger.info("Extensions registered")


class ContextualFilter(logging.Filter):
    def filter(self, log_record):
        """Provide some extra variables to be placed into the log message."""

        # If we have an app context (because we're servicing an http request) then get the trace id we have
        # set in g (see app.py)
        # Also get other useful information about the request and session
        if ctx.has_app_context():
            log_record.trace_id = g.trace_id
            # Augment log message with additional information
            if hasattr(g, 'session'):
                user_id = g.session.user.id
            else:
                user_id = "N/A"
            log_record.msg = "Endpoint: {}, Method: {}, User ID: {}, Caller: {}.{}[{}], {}".format(
                request.endpoint, request.method, user_id, log_record.module,
                log_record.funcName, log_record.lineno, log_record.msg)
        else:
            log_record.trace_id = 'N/A'

        return True


class JsonFormatter(logging.Formatter):
    def format(self, record):
        if record.exc_info:
            exc = traceback.format_exception(*record.exc_info)
        else:
            exc = None
        # Timestamp must be first (webops request)
        log_entry = collections.OrderedDict(
            [('timestamp', self.formatTime(record)),
             ('level', record.levelname),
             ('traceid', record.trace_id),
             ('message', record.msg % record.args),
             ('exception', exc)])

        return json.dumps(log_entry)


class JsonAuditFormatter(logging.Formatter):
    def format(self, record):
        # Timestamp must be first (webops request)
        log_entry = collections.OrderedDict(
            [('timestamp', self.formatTime(record)),
             ('level', 'AUDIT'),
             ('traceid', record.trace_id),
             ('message', record.msg % record.args)])

        return json.dumps(log_entry)
