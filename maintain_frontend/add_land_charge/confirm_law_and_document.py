from flask import render_template, redirect, url_for, g, current_app
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions


def register_routes(bp):
    bp.add_url_rule('/add-local-land-charge/confirm-law-and-legal-document',
                    view_func=get_law_document_confirmation, methods=['GET'])
    bp.add_url_rule('/add-local-land-charge/law-and-legal-document-confirmed',
                    view_func=law_document_confirmed, methods=['GET'])


@requires_permission([Permissions.add_llc])
def get_law_document_confirmation():
    if g.session.add_charge_state is None or \
       g.session.add_charge_state.charge_type is None or \
       g.session.add_charge_state.statutory_provision is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_land_charge.new"))
        return redirect(url_for("add_land_charge.new"))

    current_app.logger.info("Displaying page 'confirm_law_and_document.html'")
    return render_template('confirm_law_and_document.html',
                           law=g.session.add_charge_state.statutory_provision,
                           document=g.session.add_charge_state.instrument)


@requires_permission([Permissions.add_llc])
def law_document_confirmed():

    if g.session.add_charge_state is None \
            or g.session.add_charge_state.charge_type is None \
            or g.session.add_charge_state.statutory_provision is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_land_charge.new"))
        return redirect(url_for("add_land_charge.new"))

    return where_to_next(g.session.add_charge_state.charge_type)


def where_to_next(category):
    if category == 'Financial':
        next_url = url_for("add_land_charge.get_financial_charge")
    elif category == 'Land compensation':
        next_url = url_for("add_land_charge.get_land_compensation_type")
    elif category == "Light obstruction notice":
        next_url = url_for("add_lon.new")
    else:
        next_url = url_for("add_land_charge.get_charge_date")
    current_app.logger.info("Redirecting to next step: %s", next_url)
    return redirect(next_url)
