from flask import current_app, g, url_for, redirect
from maintain_frontend.models import LLC1Search
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions


def register_routes(bp):
    bp.add_url_rule('/create-official-search', view_func=create_llc1, methods=['GET'])


@requires_permission([Permissions.request_llc1])
def create_llc1():
    current_app.logger.info('Create LLC1 endpoint called')
    g.session.llc1_state = LLC1Search()
    g.session.commit()

    current_app.logger.info("Redirecting to: %s", url_for("create_llc1.llc1_get_location"))
    return redirect(url_for("create_llc1.llc1_get_location"))
