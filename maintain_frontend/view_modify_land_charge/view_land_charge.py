from flask import current_app, render_template, g, redirect, url_for
from maintain_frontend.dependencies.audit_api.audit_api import AuditAPIService
from maintain_frontend.dependencies.search_api.local_land_charge_service import LocalLandChargeService
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.services.charge_id_services import validate_charge_id
from maintain_frontend.services.charge_services import get_history_update_info_by_charge_id
from maintain_frontend.constants.lon_defaults import LonDefaults
import json


def register_routes(bp):
    bp.add_url_rule('/<local_land_charge>', view_func=view_land_charge, methods=['GET'])


@requires_permission([Permissions.retrieve_llc])
def view_land_charge(local_land_charge):
    current_app.logger.info("Endpoint called - Clearing session charge")

    local_land_charge_service = LocalLandChargeService(current_app.config)

    # Clear these session values if someone quit an edit back to the view page
    g.session.add_charge_state = None
    g.session.edited_fields = None
    g.session.charge_added_outside_users_authority = None
    g.session.other_authority_update_permission = None
    g.session.other_authority_cancel_permission = None
    g.session.commit()
    current_app.logger.info("Charge cleared from session")

    validate_charge_id(local_land_charge)

    current_app.logger.info("Retrieving charge for local_land_charge='{}'".format(local_land_charge))
    response = local_land_charge_service.get_by_charge_number(local_land_charge)

    if response.status_code == 404:
        current_app.logger.info("Search service reports '{}' not found - Returning error".format(local_land_charge))
        raise ApplicationError(404)

    response.raise_for_status()
    current_app.logger.info("Retrieved charge for local_land_charge='{}'".format(local_land_charge))

    charge_data = response.json()[0]['item']
    charge_item = LocalLandChargeItem.from_json(charge_data)

    # Let the LON blueprint handle LONS
    if charge_item.charge_type == LonDefaults.charge_type:
        return redirect(url_for('view_lon.view_lon', charge_id=local_land_charge))

    current_app.logger.info("Retrieving charge history for local_land_charge='{}'".format(local_land_charge))
    updated, updated_date = get_history_update_info_by_charge_id(local_land_charge, local_land_charge_service)

    current_app.logger.info("Rendering template for local_land_charge='{}'".format(local_land_charge))
    AuditAPIService.audit_event("User viewing charge: {}".format(local_land_charge))

    return render_template('view_charge.html', charge_item=charge_item, charge_id=response.json()[0]['display_id'],
                           updated_date=updated_date, updated=updated, geometry=json.dumps(charge_item.geometry))
