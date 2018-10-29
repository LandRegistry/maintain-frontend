from flask import current_app, render_template
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.dependencies.search_api.local_land_charge_service import LocalLandChargeService
from maintain_frontend.view_modify_land_charge.view_land_charge import validate_charge_id
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.models import LocalLandChargeHistoryItem, LocalLandChargeItem
from maintain_frontend.constants.lon_defaults import LonDefaults
from maintain_frontend.services.date_formatter import DateFormatter


def register_routes(bp):
    bp.add_url_rule('/<charge_id>/history', view_func=history, methods=['GET'])
    bp.add_app_template_filter(history_change_overview_format, 'history_change_overview_format')


@requires_permission([Permissions.retrieve_llc])
def history(charge_id):

    llc_service = LocalLandChargeService(current_app.config)
    validate_charge_id(charge_id)

    history_response = llc_service.get_history_for_charge(charge_id)
    search_response = llc_service.get_by_charge_number(charge_id)

    if history_response.status_code == 404 or search_response.status_code == 404:
        current_app.logger.warning("Charge not found for charge_id='{}' - Returning not found".format(charge_id))
        raise ApplicationError(404)

    if history_response.status_code == 500 or search_response.status_code == 500:
        current_app.logger.error("Server error occurred when getting details for charge_id''{}".format(charge_id))
        raise ApplicationError(500)

    history_response.raise_for_status()
    search_response.raise_for_status()

    history_items = list(reversed(LocalLandChargeHistoryItem.from_json(history_response.json())))

    charge_data = search_response.json()[0]['item']
    land_charge = LocalLandChargeItem.from_json(charge_data)

    return render_template('view_charge_history.html', charge_id=charge_id,
                           history=history_items, local_land_charge=land_charge,
                           format_date_bst=DateFormatter.format_date_bst)


# Custom Filters
# @view_llc_bp.app_template_filter('history_change_overview_format')
def history_change_overview_format(local_land_charge_history, charge_type=None):
    item_changes = local_land_charge_history.item_changes
    cancelled = local_land_charge_history.cancelled

    # Ignore author changes
    if item_changes:
        item_changes.pop('author', None)

    if not item_changes:
        return "No changes made"

    if cancelled:
        return "Charge is cancelled"

    display_names = {
        "applicant-name": "Name: person applying for the light obstruction notice",
        "applicant-address": "Address: person applying for the light obstruction notice",
        "charge-creation-date": "Creation date",
        "charge-geographic-description": "Location",
        "documents-filed": "Legal Document(s)",
        "expiry-date": "Expiry date",
        "further-information-location": "Source information",
        "further-information-reference": "Authority reference",
        "geometry": "Extent",
        "instrument": "Source",
        "statutory-provision": "Law",
        "structure-position-and-dimension": "Height and extent: Planned development",
        "servient-land-interest-description": "Interest in the land",
        "tribunal-temporary-certificate-date": "Temporary certificate date",
        "tribunal-temporary-certificate-expiry-date": "Temporary expiry date",
        "tribunal-definitive-certificate-date": "Definitive certificate date",
        "supplementary-information": "Description",
        "land-compensation-paid": "Advance payment",
        "land-compensation-amount-type": "Agreed or estimated",
        "amount-of-compensation": "Total compensation"
    }

    if charge_type == LonDefaults.charge_type:
        display_names["charge-geographic-description"] = "Address - Dominant building"

    changes_overview = []

    for key in item_changes:
        if key in display_names:
            changes_overview.append(display_names[key])
        else:
            # Remove dash and capitalize if required
            change = key.replace("-", " ").title()
            changes_overview.append(change)

    changes_overview = sorted(changes_overview)

    return ', <br>'.join(changes_overview)
