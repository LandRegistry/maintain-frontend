from flask import g, current_app, render_template, url_for, redirect
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.dependencies.search_api.local_land_charge_service import LocalLandChargeService
from maintain_frontend.dependencies.audit_api.audit_api import AuditAPIService
from maintain_frontend.dependencies.maintain_api.maintain_api_service import MaintainApiService
from maintain_frontend.services.charge_services import get_history_update_info_by_charge_id
from maintain_frontend.services.charge_id_services import calc_display_id
import json


def register_routes(bp):
    bp.add_url_rule('/<charge_id>/confirm-changes', view_func=modify_lon_details_get, methods=['GET'])
    bp.add_url_rule('/<charge_id>/confirm-changes', view_func=modify_land_charge_confirm, methods=['POST'])
    bp.add_url_rule('/<charge_id>/changes-saved', view_func=modify_confirmation, methods=['GET'])
    bp.add_url_rule('/<charge_id>/clear-changes', view_func=clear_lon_changes, methods=['GET'])


@requires_permission([Permissions.vary_lon])
def modify_lon_details_get(charge_id):
    current_app.logger.info("Endpoint called with charge_id='{}'".format(charge_id))

    # If the charge not in session, redirect to initial upload screen
    if not g.session.add_lon_charge_state:
        return redirect(url_for("modify_lon.modify_lon_upload_get", charge_id=charge_id))

    session_charge_id = calc_display_id(g.session.add_lon_charge_state.local_land_charge)

    # Check that charge ID in session and URL match.
    # If they don't, redirect user to the charge ID they entered and clear session
    if session_charge_id != charge_id:
        g.session.add_lon_charge_state = None
        g.session.commit()
        return redirect(url_for("modify_lon.modify_lon_upload_get", charge_id=charge_id))

    # Retrieve Light Obstruction Notice Item
    local_land_charge_service = LocalLandChargeService(current_app.config)

    charge_item = g.session.add_lon_charge_state
    updated, updated_date = get_history_update_info_by_charge_id(charge_id, local_land_charge_service)

    return render_template("modify_lon_details.html", charge_id=charge_id, charge_item=charge_item,
                           updated=updated, updated_date=updated_date,
                           geometry=json.dumps(charge_item.geometry))


@requires_permission([Permissions.vary_lon])
def modify_land_charge_confirm(charge_id):
    current_app.logger.info("Endpoint called - Updating charge")

    AuditAPIService.audit_event("Vary request submitted", supporting_info={'id': charge_id})
    MaintainApiService.update_charge(g.session.add_lon_charge_state)

    g.session.add_lon_charge_state = None
    g.session.edited_fields = None
    g.session.commit()

    current_app.logger.info("Charge removed from session - Rendering Template")
    # This is required because if the render_template is called from this post method then the flow won't be able to
    # return to the confirmation page if the user goes to the feedback form from the confirmation page
    return redirect(url_for('modify_lon.modify_confirmation', charge_id=charge_id))


@requires_permission([Permissions.vary_lon])
def modify_confirmation(charge_id):
    return render_template('modify_confirmation.html', charge_id=charge_id)


@requires_permission([Permissions.vary_lon])
def clear_lon_changes(charge_id):
    g.session.add_lon_charge_state = None
    g.session.edited_fields = {}
    g.session.commit()
    current_app.logger.info("Charge cleared from session")
    return redirect(url_for('modify_lon.modify_lon_upload_get', charge_id=charge_id))
