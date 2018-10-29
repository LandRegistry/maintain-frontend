from flask import render_template, redirect, url_for, request, g, current_app

from maintain_frontend.add_land_charge.validation.statutory_provisions_validator import StatutoryProvisionsValidator
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.decorators import requires_permission
from maintain_frontend.dependencies.maintain_api.categories import CategoryService


def register_routes(bp):
    bp.add_url_rule('/add-local-land-charge/choose-law', view_func=get_law, methods=['GET'])
    bp.add_url_rule('/add-local-land-charge/choose-law', view_func=post_law, methods=['POST'])
    bp.add_url_rule('/add-local-land-charge/search-law', view_func=search_law, methods=['GET'])
    bp.add_url_rule('/add-local-land-charge/search-law', view_func=post_search_law, methods=['POST'])


@requires_permission([Permissions.add_llc])
def get_law():
    if g.session.add_charge_state is None or g.session.add_charge_state.charge_type is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_land_charge.new"))
        return redirect(url_for("add_land_charge.new"))

    if g.session.category_details is None \
            or g.session.category_details.statutory_provisions is None \
            or len(g.session.category_details.statutory_provisions) == 0:
        current_app.logger.info("Redirecting to: %s", url_for("add_land_charge.new"))
        return redirect(url_for("add_land_charge.new"))

    current_app.logger.info("Displaying page 'confirm_law.html'")
    return render_template('confirm_law.html',
                           laws=g.session.category_details.statutory_provisions,
                           category=g.session.category_details.display_name)


@requires_permission([Permissions.add_llc])
def post_law():

    if g.session.add_charge_state is None or g.session.add_charge_state.charge_type is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_land_charge.new"))
        return redirect(url_for("add_land_charge.new"))

    if g.session.category_details is None \
            or g.session.category_details.statutory_provisions is None \
            or len(g.session.category_details.statutory_provisions) == 0:
        current_app.logger.info("Redirecting to: %s", url_for("add_land_charge.new"))
        return redirect(url_for("add_land_charge.new"))

    law = request.form.get('confirm-law-option')

    current_app.logger.info("Running validation")
    validation_errors = StatutoryProvisionsValidator.validate(law)

    if validation_errors.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template(
            'confirm_law.html',
            validation_errors=validation_errors.errors,
            laws=g.session.category_details.statutory_provisions,
            category=g.session.category_details.display_name,
            validation_summary_heading=validation_errors.summary_heading_text), 400

    g.session.add_charge_state.statutory_provision = law
    g.session.category_confirmation = False
    g.session.commit()

    return where_to_next()


@requires_permission([Permissions.add_llc])
def search_law():
    if g.session.add_charge_state is None or g.session.add_charge_state.charge_type is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_land_charge.new"))
        return redirect(url_for("add_land_charge.new"))

    provisions = CategoryService.get_all_stat_provs()

    current_app.logger.info("Displaying page 'search_law.html'")
    return render_template('search_law.html',
                           provisions=provisions)


@requires_permission([Permissions.add_llc])
def post_search_law():
    if g.session.add_charge_state is None or g.session.add_charge_state.charge_type is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_land_charge.new"))
        return redirect(url_for("add_land_charge.new"))

    if 'legislation-nojs' in request.form:
        provision = request.form['legislation-nojs'].strip()
    elif 'legislation' in request.form:
        provision = request.form['legislation'].strip()
    else:
        provision = ''

    provisions = CategoryService.get_all_stat_provs()

    validation_errors = StatutoryProvisionsValidator.validate(provision, provisions)

    if validation_errors.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template('search_law.html',
                               provisions=provisions,
                               current_provision=provision,
                               validation_errors=validation_errors.errors,
                               validation_summary_heading=validation_errors.summary_heading_text), 400

    g.session.add_charge_state.statutory_provision = provision
    g.session.category_confirmation = False
    g.session.commit()

    return where_to_next()


def where_to_next():
    if g.session.add_charge_state.charge_sub_category == 'Ancient monuments':
        if '1(9)' in g.session.add_charge_state.statutory_provision:
            g.session.category_details.instruments = ['Schedule']
            g.session.add_charge_state.instrument = 'Schedule'
        elif '8(6)' in g.session.add_charge_state.statutory_provision:
            g.session.category_details.instruments = ['Notice']
            g.session.add_charge_state.instrument = 'Notice'
        elif '12(7)' in g.session.add_charge_state.statutory_provision:
            g.session.category_details.instruments = ['Deed']
            g.session.add_charge_state.instrument = 'Deed'
        elif '33(5)' in g.session.add_charge_state.statutory_provision:
            g.session.category_details.instruments = ['Order']
            g.session.add_charge_state.instrument = 'Order'
        g.session.commit()

    if len(g.session.category_details.instruments) == 0:
        next_url = url_for('add_land_charge.get_all_legal_document')
    elif len(g.session.category_details.instruments) > 1:
        next_url = url_for("add_land_charge.get_legal_document")
    elif g.session.add_charge_state.charge_type == 'Financial':
        next_url = url_for("add_land_charge.get_financial_charge")
    elif g.session.add_charge_state.charge_type == 'Land compensation':
        next_url = url_for("add_land_charge.get_land_compensation_type")
    elif g.session.add_charge_state.charge_type == "Light obstruction notice":
        next_url = url_for("add_lon.new")
    else:
        next_url = url_for("add_land_charge.get_charge_date")
    current_app.logger.info("Redirecting to next step: %s", next_url)
    return redirect(next_url)
