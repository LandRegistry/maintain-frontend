from flask import redirect, url_for, g, current_app
from maintain_frontend.models import SearchDetails


def register_routes(bp):
    bp.add_url_rule('/view-official-search', view_func=new, methods=['GET'])


def new():
    """This will setup state for viewing a search and redirect to the starting page."""
    g.session.search_details = SearchDetails()

    g.session.commit()
    current_app.logger.info("Created new session object: {}".format(g.session.search_details.to_json()))

    current_app.logger.info("Redirecting to: {}".format(url_for("view_official_search.get_enter_search_ref")))
    return redirect(url_for("view_official_search.get_enter_search_ref"))
