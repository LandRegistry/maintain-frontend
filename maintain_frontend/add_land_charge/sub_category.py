from flask import render_template, redirect, url_for, request, g, current_app

from maintain_frontend.add_land_charge.validation.charge_subcategory_validator import ChargeSubCategoryValidator
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.decorators import requires_permission
from maintain_frontend.dependencies.maintain_api.categories import CategoryService


def register_routes(bp):
    bp.add_url_rule('/add-local-land-charge/choose-sub-category', view_func=get_sub_category, methods=['GET'])
    bp.add_url_rule('/add-local-land-charge/choose-sub-category', view_func=post_sub_category, methods=['POST'])


@requires_permission([Permissions.add_llc])
def get_sub_category():
    if g.session.add_charge_state is None or g.session.add_charge_state.charge_type is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_land_charge.new"))
        return redirect(url_for("add_land_charge.new"))

    reset_sub_category_info()

    current_category = g.session.add_charge_state.charge_type

    category_info = CategoryService.get_category_parent_info(current_category)

    g.session.category_details = category_info
    g.session.commit()

    if len(category_info.sub_categories) > 0:
        current_app.logger.info("Displaying page 'sub_categories.html'")
        return render_template('sub_categories.html',
                               categories=category_info.sub_categories,
                               parent=category_info.display_name.lower())

    setup_session_for_instruments_and_provision(category_info)

    return where_to_next(category_info)


@requires_permission([Permissions.add_llc])
def post_sub_category():
    if g.session.add_charge_state is None or g.session.add_charge_state.charge_type is None:
        current_app.logger.info("Redirecting to: %s", url_for("add_land_charge.new"))
        return redirect(url_for("add_land_charge.new"))

    category = request.form.get('charge-sub-category')

    current_app.logger.info("Running validation")
    validation_errors = ChargeSubCategoryValidator.validate(category)

    if validation_errors.errors:
        current_app.logger.warning("Validation errors occurred")
        category_info = CategoryService.get_category_parent_info(g.session.category_details.name)
        return render_template(
            'sub_categories.html',
            validation_errors=validation_errors.errors,
            categories=category_info.sub_categories,
            parent=category_info.display_name.lower(),
            validation_summary_heading=validation_errors.summary_heading_text), 400

    if category == "I don't know the charge category":
        return redirect(url_for('add_land_charge.get_subcategory_not_known'))

    current_app.logger.info("Updating session object with charge sub-category: %s", category)
    g.session.add_charge_state.charge_sub_category = category
    category_info = CategoryService.get_sub_category_info(g.session.category_details.name, category)
    g.session.category_details = category_info
    g.session.commit()

    if len(category_info.sub_categories) > 0:
        current_app.logger.info("Displaying page 'sub_categories.html'")
        return render_template('sub_categories.html',
                               categories=category_info.sub_categories,
                               parent=category_info.display_name.lower())

    setup_session_for_instruments_and_provision(category_info)

    return where_to_next(category_info)


def where_to_next(details):
    if details.name == 'Land compensation':
        next_url = url_for("add_land_charge.get_all_legal_document")
    elif len(details.statutory_provisions) == 0:
        next_url = url_for('add_land_charge.search_law')
    elif len(details.statutory_provisions) > 1:
        next_url = url_for('add_land_charge.get_law')
    elif len(details.instruments) == 0:
        next_url = url_for('add_land_charge.get_all_legal_document')
    elif len(details.instruments) > 1:
        next_url = url_for('add_land_charge.get_legal_document')
    elif details.name == "Light obstruction notice":
        next_url = url_for("add_lon.new")
    else:
        next_url = url_for('add_land_charge.get_law_document_confirmation')
    current_app.logger.info("Redirecting to next step: %s", next_url)
    return redirect(next_url)


def setup_session_for_instruments_and_provision(details):
    if len(details.statutory_provisions) == 1:
        g.session.add_charge_state.statutory_provision = details.statutory_provisions[0]
        g.session.category_confirmation = True

    if len(details.instruments) == 1:
        g.session.add_charge_state.instrument = details.instruments[0]

    g.session.commit()


def reset_sub_category_info():
    g.session.add_charge_state.charge_sub_category = None
    g.session.add_charge_state.statutory_provision = None
    g.session.add_charge_state.instrument = None
    g.session.category_confirmation = None
    g.session.category_details = None
    g.session.commit()
