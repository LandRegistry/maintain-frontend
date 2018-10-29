from flask import render_template, redirect, url_for, request, g, current_app

from maintain_frontend.add_land_charge.validation.legal_document_validator import LegalDocumentValidator
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.decorators import requires_permission
from maintain_frontend.dependencies.maintain_api.categories import CategoryService


def register_routes(bp):
    bp.add_url_rule('/add-local-land-charge/confirm-legal-document',
                    view_func=get_legal_document, methods=['GET'])
    bp.add_url_rule('/add-local-land-charge/confirm-legal-document',
                    view_func=post_legal_document, methods=['POST'])
    bp.add_url_rule('/add-local-land-charge/select-legal-document',
                    view_func=get_all_legal_document, methods=['GET'])
    bp.add_url_rule('/add-local-land-charge/select-legal-document',
                    view_func=post_all_legal_document, methods=['POST'])


@requires_permission([Permissions.add_llc])
def get_legal_document():
    if g.session.add_charge_state is None or g.session.add_charge_state.charge_type is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_land_charge.new"))
        return redirect(url_for("add_land_charge.new"))

    if g.session.category_details is None \
            or g.session.category_details.instruments is None \
            or len(g.session.category_details.instruments) == 0:
        current_app.logger.info("Redirecting to: %s", url_for("add_land_charge.new"))
        return redirect(url_for("add_land_charge.new"))

    current_app.logger.info("Displaying page 'confirm_law.html'")
    return render_template('confirm_legal_document.html',
                           instruments=g.session.category_details.instruments,
                           law=g.session.add_charge_state.statutory_provision)


@requires_permission([Permissions.add_llc])
def post_legal_document():

    if g.session.add_charge_state is None or g.session.add_charge_state.charge_type is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_land_charge.new"))
        return redirect(url_for("add_land_charge.new"))

    if g.session.category_details is None \
            or g.session.category_details.instruments is None \
            or len(g.session.category_details.instruments) == 0:
        current_app.logger.info("Redirecting to: %s", url_for("add_land_charge.new"))
        return redirect(url_for("add_land_charge.new"))

    instrument = request.form.get('confirm-instrument')

    current_app.logger.info("Running validation")
    validation_errors = LegalDocumentValidator.validate(instrument)

    if validation_errors.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template(
            'confirm_legal_document.html',
            validation_errors=validation_errors.errors,
            instruments=g.session.category_details.instruments,
            law=g.session.add_charge_state.statutory_provision,
            validation_summary_heading=validation_errors.summary_heading_text), 400

    if instrument is not None:
        g.session.add_charge_state.instrument = instrument
        g.session.commit()

    return where_to_next(g.session.add_charge_state.charge_type)


@requires_permission([Permissions.add_llc])
def get_all_legal_document():
    if g.session.add_charge_state is None or g.session.add_charge_state.charge_type is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_land_charge.new"))
        return redirect(url_for("add_land_charge.new"))

    instruments = CategoryService.get_all_instruments()

    current_app.logger.info("Displaying page 'instruments.html'")
    return render_template('instruments.html',
                           instruments=instruments)


@requires_permission([Permissions.add_llc])
def post_all_legal_document():

    if g.session.add_charge_state is None or g.session.add_charge_state.charge_type is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_land_charge.new"))
        return redirect(url_for("add_land_charge.new"))

    if 'confirm-instrument' in request.form:
        g.session.add_charge_state.instrument = request.form.get('confirm-instrument')
        g.session.commit()

    return where_to_next(g.session.add_charge_state.charge_type)


def where_to_next(category):
    if g.session.category_confirmation:
        next_url = url_for('add_land_charge.get_law_document_confirmation')
    elif category == 'Financial':
        next_url = url_for("add_land_charge.get_financial_charge")
    elif category == 'Land compensation':
        next_url = url_for("add_land_charge.get_land_compensation_type")
    elif category == "Light obstruction notice":
        next_url = url_for("add_lon.new")
    else:
        next_url = url_for("add_land_charge.get_charge_date")
    current_app.logger.info("Redirecting to next step: %s", next_url)
    return redirect(next_url)
