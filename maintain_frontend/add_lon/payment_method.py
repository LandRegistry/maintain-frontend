from flask import g, render_template, redirect, url_for, current_app, request
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.add_lon.validation.payment_method_validator import PaymentMethodValidator


def register_routes(bp):
    bp.add_url_rule('/add-light-obstruction-notice/confirm-payment-method',
                    view_func=get_payment_method, methods=['GET'])
    bp.add_url_rule('/add-light-obstruction-notice/confirm-payment-method',
                    view_func=post_payment_method, methods=['POST'])


@requires_permission([Permissions.add_lon])
def get_payment_method():
    if g.session.add_lon_charge_state is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_lon.new"))
        return redirect(url_for("add_lon.new"))

    request_body = {}

    if g.session.payment_info.payment_method:
        request_body = {
            'payment_method': g.session.payment_info.payment_method,
            'payment_ref': g.session.payment_info.payment_ref,
            'no_payment_notes': g.session.payment_info.no_payment_notes
        }

    current_app.logger.info("Displaying page 'payment_method.html'")
    return render_template('payment_method.html',
                           request_body=request_body,
                           submit_url=url_for('add_lon.post_payment_method'))


@requires_permission([Permissions.add_lon])
def post_payment_method():
    payment_form = request.form

    current_app.logger.info("Running validation")
    validation_error_builder = PaymentMethodValidator.validate(payment_form)

    if validation_error_builder.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template('payment_method.html',
                               validation_errors=validation_error_builder.errors,
                               validation_summary_heading=validation_error_builder.summary_heading_text,
                               submit_url=url_for('add_lon.post_payment_method'),
                               request_body=payment_form), 400

    payment_method = payment_form.get('payment_method')
    payment_ref = payment_form.get('payment_ref')
    no_payment_notes = payment_form.get('no_payment_notes')

    current_app.logger.info("Updating session object")
    g.session.payment_info.payment_method = payment_method
    g.session.payment_info.payment_ref = payment_ref
    g.session.payment_info.no_payment_notes = no_payment_notes
    g.session.commit()

    return redirect(url_for('add_lon.get_applicant_info'))
