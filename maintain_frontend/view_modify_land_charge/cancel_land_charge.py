from flask import render_template, request, current_app, redirect, url_for, g
from maintain_frontend.dependencies.search_api.local_land_charge_service import LocalLandChargeService
from maintain_frontend.dependencies.local_authority_api.local_authority_api_service import LocalAuthorityService
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.dependencies.audit_api.audit_api import AuditAPIService
from maintain_frontend.dependencies.maintain_api.maintain_api_service import MaintainApiService
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.services.build_extents_from_features import build_extents_from_features
from datetime import date
import json


def register_routes(bp):
    bp.add_url_rule('/<charge_id>', view_func=cancel_charge, methods=['GET', 'POST'])
    bp.add_url_rule('/<charge_id>/charge-cancelled', view_func=cancel_confirmation, methods=['GET'])


# Cancel Page
@requires_permission([Permissions.cancel_llc])
def cancel_charge(charge_id):
    current_app.logger.info("Endpoint called with charge_id='{}'".format(charge_id))
    local_land_charge_service = LocalLandChargeService(current_app.config)
    current_app.logger.info("Retrieving charge information from charge_id='{}'".format(charge_id))
    response = local_land_charge_service.get_by_charge_number(charge_id)
    if response.status_code == 404:
        current_app.logger.warning("Charge not found for charge_id='{}' - Returning not found".format(charge_id))
        raise ApplicationError(404)
    response.raise_for_status()

    charge_data = response.json()[0]['item']
    charge_item = LocalLandChargeItem.from_json(charge_data)

    # add the charge to the session for checking the geometry is within the user's authority
    g.session.add_charge_state = charge_item
    g.session.commit()

    current_app.logger.info("Charge information retrieved for charge_id='{}'".format(charge_id))
    if request.method == 'GET':
        # Check if the charge is outside of the user's authority
        extent = build_extents_from_features(charge_item.geometry)
        result = LocalAuthorityService(current_app.config).get_authorities_by_extent(extent)

        if should_show_confirmation_warning(result):
            # In this case the charge is outside of the user's authority
            if Permissions.add_extent_anywhere in g.session.user.permissions:
                # If the user has permission to add a charge anywhere, give them cancel permission without asking
                g.session.other_authority_cancel_permission = True
                g.session.commit()

            if not g.session.other_authority_cancel_permission:
                # if the user has not confirmed that they can edit charges outside of their authority, make them
                return redirect(url_for('cancel_land_charge.get_cancel_location_confirmation'))

        current_app.logger.info("Rendering response for charge_id='{}'".format(charge_id))
        return render_template('cancel.html', charge_id=charge_id, charge_item=charge_item,
                               geometry=json.dumps(charge_item.geometry))
    else:
        charge_item.end_date = date.today()
        current_app.logger.info("Updating charge with cancellation date for charge_id='{}'".format(charge_id))
        AuditAPIService.audit_event("Cancelling charge", supporting_info={'id': charge_id})
        if g.session.other_authority_cancel_permission:
            AuditAPIService.audit_event(
                "Charge cancelled outside users authority.",
                supporting_info={'originating-authority': g.session.user.organisation})
        MaintainApiService.update_charge(charge_item)
        current_app.logger.info("Rendering response for charge_id='{}'".format(charge_id))
        # This is required because if the render_template is called from this post method then the flow won't be able
        # to return to the confirmation page if the user goes to the feedback form from the confirmation page
        return redirect(url_for('cancel_land_charge.cancel_confirmation', charge_id=charge_id))


# Cancel Page
@requires_permission([Permissions.cancel_llc])
def cancel_confirmation(charge_id):
    return render_template('charge_cancelled.html', charge_id=charge_id)


def should_show_confirmation_warning(result):
    if Permissions.add_extent_england in g.session.user.permissions:
        return len(result) == 0
    else:
        return len(result) != 1 or g.session.user.organisation not in result
