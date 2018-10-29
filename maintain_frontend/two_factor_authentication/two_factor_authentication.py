from flask import render_template, request, g, redirect, url_for
from datetime import datetime
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.services import two_factor_authentication_code_generator
from maintain_frontend.dependencies.notification_api.notification_api_service import NotificationAPIService
from maintain_frontend.dependencies.audit_api.audit_api import AuditAPIService
from maintain_frontend.two_factor_authentication.validation.\
    two_factor_authentication_validator import TwoFactorAuthenticationValidator
from maintain_frontend import config


def register_routes(bp):
    bp.add_url_rule('/check-your-email', view_func=get_check_your_email, methods=['GET'])
    bp.add_url_rule('/check-your-email', view_func=post_check_your_email, methods=['POST'])
    bp.add_url_rule('/send-a-new-code', view_func=get_send_the_code_again, methods=['GET'])
    bp.add_url_rule('/send-a-new-code', view_func=post_send_the_code_again, methods=['POST'])


@requires_permission([Permissions.account_management, Permissions.manage_source_information])
def get_check_your_email():
    if g.session.two_factor_authentication_code is None and config.ENABLE_TWO_FACTOR_AUTHENTICATION:
        g.session.two_factor_authentication_code = two_factor_authentication_code_generator.generate_code()
        g.session.two_factor_authentication_generation_time = get_current_timestamp_minutes()
        g.session.two_factor_authentication_invalid_attempts = 0
        g.session.commit_2fa_state()

        NotificationAPIService.send_message_notify(
            g.session.user.email,
            config.NOTIFY_TWO_FACTOR_AUTH_TEMPLATE_ID,
            {'code': g.session.two_factor_authentication_code}
        )

        AuditAPIService.audit_event("2FA code sent to user")

    return render_template('check_your_email.html')


@requires_permission([Permissions.account_management, Permissions.manage_source_information])
def post_check_your_email():
    # Make sure a code and generation time has actually been set
    if g.session.two_factor_authentication_code is None or \
            g.session.two_factor_authentication_generation_time is None:
        return redirect(url_for('two_factor_authentication.get_check_your_email'))

    code = request.form.get('code')
    validation_errors = TwoFactorAuthenticationValidator.validate(code)
    if 'code' in validation_errors.errors:
        # Log user out after 3 incorrect attempts
        AuditAPIService.audit_event('Invalid entry of 2FA code')

        if g.session.two_factor_authentication_invalid_attempts and \
                g.session.two_factor_authentication_invalid_attempts >= 2:
            AuditAPIService.audit_event('2FA code attempt limits exceeded')
            return redirect('/logout')

        if g.session.two_factor_authentication_invalid_attempts:
            g.session.two_factor_authentication_invalid_attempts = \
                g.session.two_factor_authentication_invalid_attempts + 1
        else:
            g.session.two_factor_authentication_invalid_attempts = 1

        g.session.commit_2fa_state()

        return render_template(
            'check_your_email.html',
            validation_errors=validation_errors.errors,
            validation_summary_heading=validation_errors.summary_heading_text,
        ), 400

    # Check code hasn't expired and that it matches
    if (get_current_timestamp_minutes() - g.session.two_factor_authentication_generation_time) < 10 and \
            str(code) == str(g.session.two_factor_authentication_code):
        g.session.two_factor_authentication_passed = True
        g.session.commit_2fa_state()
        AuditAPIService.audit_event('User successfully passed 2FA')
        return redirect(g.session.two_factor_authentication_redirect_url)

    AuditAPIService.audit_event('Invalid entry of 2FA code')

    # Log user out after 3 incorrect attempts
    if g.session.two_factor_authentication_invalid_attempts and \
            g.session.two_factor_authentication_invalid_attempts >= 2:
        AuditAPIService.audit_event('2FA code attempt limits exceeded')
        return redirect('/logout')

    if g.session.two_factor_authentication_invalid_attempts:
        g.session.two_factor_authentication_invalid_attempts = g.session.two_factor_authentication_invalid_attempts + 1
    else:
        g.session.two_factor_authentication_invalid_attempts = 1

    g.session.commit_2fa_state()

    # Generate error for incorrect / expired code
    validation_errors = TwoFactorAuthenticationValidator.generate_invalid_code_error_message()

    return render_template(
        'check_your_email.html',
        validation_errors=validation_errors.errors,
        validation_summary_heading=validation_errors.summary_heading_text,
    ), 400


@requires_permission([Permissions.account_management, Permissions.manage_source_information])
def get_send_the_code_again():
    return render_template('send_the_code_again.html')


@requires_permission([Permissions.account_management, Permissions.manage_source_information])
def post_send_the_code_again():
    if g.session.two_factor_authentication_code:
        g.session.two_factor_authentication_code = None
        g.session.commit_2fa_state()
    return redirect(url_for('two_factor_authentication.get_check_your_email'))


def get_current_timestamp_minutes():
    return datetime.now().timestamp() / 60
