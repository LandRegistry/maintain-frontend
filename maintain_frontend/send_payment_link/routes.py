from flask import Blueprint

import maintain_frontend.send_payment_link.send_payment_link
import maintain_frontend.send_payment_link.payment_for
import maintain_frontend.send_payment_link.enter_email


# Blueprint Definition
send_payment_link_bp = Blueprint('send_payment_link', __name__,
                                 static_url_path='/static/send-payment-link',
                                 static_folder='static',
                                 template_folder='templates')


maintain_frontend.send_payment_link.send_payment_link.register_routes(send_payment_link_bp)
maintain_frontend.send_payment_link.payment_for.register_routes(send_payment_link_bp)
maintain_frontend.send_payment_link.enter_email.register_routes(send_payment_link_bp)
