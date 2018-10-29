from flask import redirect, url_for, g, current_app, render_template, request
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.send_payment_link.validation.customer_email_validator import CustomerEmailValidator
from maintain_frontend.dependencies.audit_api.audit_api import AuditAPIService
from maintain_frontend.dependencies.notification_api.notification_api_service import NotificationAPIService
from maintain_frontend import config


def register_routes(bp):
    bp.add_url_rule('/enter-email', view_func=get_enter_email, methods=['GET'])
    bp.add_url_rule('/enter-email', view_func=post_enter_email, methods=['POST'])


@requires_permission([Permissions.add_lon])
def get_enter_email():
    current_app.logger.info('Endpoint called')
    if g.session.send_payment_link_info is None:
        current_app.logger.info('Redirecting to: %s', url_for("send_payment_link.send_payment_link"))
        return redirect(url_for("send_payment_link.send_payment_link"))

    previous_data = None

    # If user information has already been set then populate for edit
    if g.session.send_payment_link_info.email is not None:
        current_app.logger.info("User information has been found, populating for edit")
        previous_data = g.session.send_payment_link_info

    current_app.logger.info("Displaying page 'enter_email.html")
    return render_template('enter_email.html',
                           request_body=previous_data,
                           submit_url=url_for("send_payment_link.post_enter_email"))


@requires_permission([Permissions.add_lon])
def post_enter_email():
    email = request.form.get('email')
    current_app.logger.info("Endpoint called with customer email as '{}'".format(email))

    validator = CustomerEmailValidator.validate(email)
    if validator.errors:
        current_app.logger.warning("Validation errors found")
        return render_template(
            'enter_email.html',
            validation_errors=validator.errors,
            validation_summary_heading=validator.summary_heading_text,
            error_heading_message=validator.summary_heading_text,
            request_body=request.form,
            submit_url=url_for("send_payment_link.post_enter_email")
        ), 400

    # Send email
    NotificationAPIService.send_message_notify(
        email,
        config.NOTIFY_PAYMENT_LINK_TEMPLATE_ID,
        {}
    )

    # Clear down the session information for payment
    g.session.send_payment_link_info = None
    g.session.commit()

    AuditAPIService.audit_event("LON payment link sent to user {}".format(email))

    return render_template('email_confirmation.html')
