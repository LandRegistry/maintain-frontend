from flask import g, render_template, redirect, url_for, current_app
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions


def register_routes(bp):
    bp.add_url_rule('/add-light-obstruction-notice/charge-added', view_func=get_confirmation, methods=['GET'])


@requires_permission([Permissions.add_lon])
def get_confirmation():
    current_app.logger.info("Endpoint called")
    if g.session.last_created_charge is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_lon.new"))
        return redirect(url_for("add_lon.new"))

    current_app.logger.info("Clearing out session object")
    g.session.add_lon_charge_state = None
    g.session.payment_info = None
    g.session.filenames = None
    g.session.commit()

    current_app.logger.info("Displaying page 'confirmation.html'")
    return render_template('confirmation.html', data=g.session.last_created_charge)
