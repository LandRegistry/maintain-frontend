from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from flask import current_app, g, url_for, redirect, render_template, request
from maintain_frontend.llc1.validation.search_description_validator import SearchDescriptionValidator
from maintain_frontend.services.address_converter import AddressConverter
import json


def register_routes(bp):
    bp.add_url_rule('/create-official-search/search-area-description',
                    view_func=llc1_get_description, methods=['GET'])
    bp.add_url_rule('/create-official-search/search-area-description',
                    view_func=llc1_set_description, methods=['POST'])


@requires_permission([Permissions.request_llc1])
def llc1_get_description():
    current_app.logger.info('Endpoint called')
    if g.session.llc1_state is None:
        current_app.logger.info('Redirecting to: %s', url_for("create_llc1.create_llc1"))
        return redirect(url_for("create_llc1.create_llc1"))

    current_app.logger.info("Render template 'search_description.html'")
    return render_template('search_description.html',
                           submit_url=url_for('create_llc1.llc1_set_description'))


@requires_permission([Permissions.request_llc1])
def llc1_set_description():
    current_app.logger.info('Endpoint called')
    if g.session.llc1_state is None:
        current_app.logger.info('Redirecting to: %s', url_for("create_llc1.create_llc1"))
        return redirect(url_for("create_llc1.create_llc1"))

    has_address = request.form.get('has-address')
    information = None
    address = request.form.get('selected-address')

    if has_address is not None and has_address.strip() == 'No':
        information = request.form['charge-geographic-description'].strip()
    elif has_address is not None and \
            has_address.strip() == 'ProvideAddress' and \
            address is not None and \
            address != '':
        charge_address = AddressConverter.to_charge_address(json.loads(address))
        information = AddressConverter.get_display_address(charge_address)

    current_app.logger.info("Running validation")
    validation_errors = SearchDescriptionValidator.validate(information, has_address)

    if validation_errors.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template('search_description.html',
                               validation_errors=validation_errors.errors,
                               validation_summary_heading=validation_errors.summary_heading_text,
                               data=information,
                               has_address=has_address,
                               submit_url=url_for("create_llc1.llc1_set_description")), 400

    current_app.logger.info("Updating session object")
    g.session.llc1_state.description = information
    g.session.commit()

    current_app.logger.info("Redirecting to next step: %s", url_for("create_llc1.llc1_get_result"))
    return redirect(url_for("create_llc1.llc1_get_result"))
