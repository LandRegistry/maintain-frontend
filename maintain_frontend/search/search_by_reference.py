from flask import render_template, current_app, request, url_for, redirect, g
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.decorators import requires_permission
from maintain_frontend.search.validation.reference_validator import ReferenceValidator
from maintain_frontend.services.search_by_reference import SearchByReference
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.services.charge_id_services import calc_display_id
from operator import attrgetter


def register_routes(bp):
    bp.add_url_rule('/search/reference', view_func=get_search_by_reference, methods=['GET'])
    bp.add_url_rule('/search/reference', view_func=post_search_by_reference, methods=['POST'])


@requires_permission([Permissions.browse_llc])
def get_search_by_reference():
    current_app.logger.info("Search by reference page requested")
    return render_template('search-by-reference.html', submit_url=url_for("search.post_search_by_reference"))


@requires_permission([Permissions.browse_llc])
def post_search_by_reference():
    search_reference = request.form.get('search-reference').strip()

    current_app.logger.info("Running validation")
    validation_errors = ReferenceValidator.validate(search_reference)

    if validation_errors.errors:
        current_app.logger.warning("Validation errors occurred")
        return render_template('search-by-reference.html',
                               validation_errors=validation_errors.errors,
                               validation_summary_heading=validation_errors.summary_heading_text,
                               submit_url=url_for("search.post_search_by_reference")), 400

    search_by_reference_processor = SearchByReference(current_app.config, current_app.logger)
    response = search_by_reference_processor.process(search_reference.upper())

    if response["status_code"] == 200:
        charge_items = list(map(lambda charge: LocalLandChargeItem.from_json(charge["item"]), response["results"]))

        if len(charge_items) == 1:
            return redirect(url_for('view_land_charge.view_land_charge',
                                    local_land_charge=calc_display_id(charge_items[0].local_land_charge)))
        else:
            charges_by_type = sorted(charge_items, key=attrgetter('charge_type'))
            matching_authority = list(filter(
                lambda charge_item: charge_item.originating_authority == g.session.user.organisation, charges_by_type))
            other_charges = list(filter(
                lambda charge_item: charge_item.originating_authority != g.session.user.organisation, charges_by_type))
            charge_items = matching_authority + other_charges
    else:
        charge_items = None

    return render_template('search-by-reference.html', submit_url=url_for("search.post_search_by_reference"),
                           charge_items=charge_items)
