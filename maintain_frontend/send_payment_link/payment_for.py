from flask import redirect, url_for, g, current_app, render_template, request
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.send_payment_link.validation.payment_reason_validator import PaymentReasonValidator


def register_routes(bp):
    bp.add_url_rule('/payment-for', view_func=get_payment_for, methods=['GET'])
    bp.add_url_rule('/payment-for', view_func=post_payment_for, methods=['POST'])


@requires_permission([Permissions.add_lon])
def get_payment_for():
    current_app.logger.info('Endpoint called')
    if g.session.send_payment_link_info is None:
        current_app.logger.info('Redirecting to: %s', url_for("send_payment_link.send_payment_link"))
        return redirect(url_for("send_payment_link.send_payment_link"))

    current_app.logger.info("Displaying page 'payment_for.html")
    return render_template('payment_for.html',
                           request_body=None,
                           submit_url=url_for("send_payment_link.post_payment_for"))


@requires_permission([Permissions.add_lon])
def post_payment_for():
    payment_for = request.form.get('payment_for')
    current_app.logger.info("Endpoint called with payment for '{}'".format(payment_for))

    validator = PaymentReasonValidator.validate(payment_for)
    if validator.errors:
        current_app.logger.warning("Validation errors found")
        return render_template(
            'payment_for.html',
            validation_errors=validator.errors,
            validation_summary_heading=validator.summary_heading_text,
            error_heading_message=validator.summary_heading_text,
            request_body=request.form,
            submit_url=url_for("send_payment_link.post_payment_for")
        ), 400

    if payment_for == 'lon':
        return redirect(url_for("send_payment_link.get_enter_email"))
    else:
        # TODO(official_search) replace with functional code for an official search, in a later story
        return redirect(url_for("home.get"))
