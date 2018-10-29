from flask import redirect, url_for, g, current_app
from maintain_frontend.models import PaymentLink


def register_routes(bp):
    bp.add_url_rule('/send-payment-link', view_func=send_payment_link, methods=['GET'])


def send_payment_link():
    current_app.logger.info('Endpoint called')
    g.session.send_payment_link_info = PaymentLink()
    g.session.commit()

    current_app.logger.info("Redirecting to: %s", url_for("send_payment_link.get_payment_for"))
    return redirect(url_for("send_payment_link.get_payment_for"))
