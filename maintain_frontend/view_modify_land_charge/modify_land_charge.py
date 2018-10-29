from flask import g, current_app, render_template, redirect, url_for
from maintain_frontend.dependencies.audit_api.audit_api import AuditAPIService
from maintain_frontend.dependencies.maintain_api.maintain_api_service import MaintainApiService
from maintain_frontend.dependencies.search_api.local_land_charge_service import LocalLandChargeService
from maintain_frontend.dependencies.local_authority_api.local_authority_api_service import LocalAuthorityService
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.services.charge_id_services import calc_display_id
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.services.charge_id_services import validate_charge_id
from maintain_frontend.services.charge_services import get_history_update_info_by_charge_id
from maintain_frontend.services.field_utilities import get_ordered_edited_fields
from maintain_frontend.services.build_extents_from_features import build_extents_from_features
from maintain_frontend.view_modify_land_charge.enumerations.review_map import ReviewMap
import json


def register_routes(bp):
    bp.add_url_rule('/<local_land_charge>', view_func=modify_land_charge, methods=['GET'])
    bp.add_url_rule('/<local_land_charge>/clear-changes', view_func=clear_land_charge_changes, methods=['GET'])
    bp.add_url_rule('/changes-saved', view_func=modify_land_charge_confirm, methods=['POST'])


@requires_permission([Permissions.vary_llc])
def modify_land_charge(local_land_charge):
    current_app.logger.info("Endpoint called with local_land_charge='{}'".format(local_land_charge))

    validate_charge_id(local_land_charge)

    local_land_charge_service = LocalLandChargeService(current_app.config)
    response = local_land_charge_service.get_by_charge_number(local_land_charge)

    if response.status_code == 404:
        current_app.logger.warning("Charge not found for local_land_charge='{}' - Returning not found"
                                   .format(local_land_charge))
        raise ApplicationError(404)

    response.raise_for_status()

    updated, updated_date = get_history_update_info_by_charge_id(local_land_charge, local_land_charge_service)

    if not g.session.add_charge_state:
        current_app.logger.info("Retrieving charge with local_land_charge='{}'".format(local_land_charge))
        # If the charge does not exist in the session, load it from the database, otherwise we are in the
        # process of updating it and as such it should be loaded from the session data

        charge_data = response.json()[0]['item']
        charge_item = LocalLandChargeItem.from_json(charge_data)

        current_app.logger.info("Charge information retrieved for local_land_charge='{}' - Updating session charge"
                                .format(local_land_charge))

        g.session.add_charge_state = charge_item
        g.session.edited_fields = []
        g.session.commit()

        current_app.logger.info("Session charge updated - Rendering Template")
    else:
        charge_id = calc_display_id(g.session.add_charge_state.local_land_charge)
        current_app.logger.info('charge_id: {}'.format(charge_id))
        current_app.logger.info('local_land_charge: {}'.format(local_land_charge))

        # Check that charge ID in session and URL match.
        # If they don't, redirect user to the charge ID they entered and clear session
        if charge_id != local_land_charge:
            g.session.add_charge_state = None
            g.session.edited_fields = None
            g.session.commit()
            return modify_land_charge(local_land_charge)

        charge_item = g.session.add_charge_state

        current_app.logger.info("Session charge updated - Rendering Template")

    # Check that charge hasn't been cancelled in case user attempts to navigate to update URL manually
    if charge_item.end_date:
        current_app.logger.error('Attempted to update a cancelled charge.  Charge ID: {}'.format(local_land_charge))
        raise ApplicationError(500)

    # Check if the charge is outside of the user's authority, if user hasn't already updated the map
    if not g.session.charge_added_outside_users_authority:
        extent = build_extents_from_features(charge_item.geometry)
        result = LocalAuthorityService(current_app.config).get_authorities_by_extent(extent)

        if should_show_confirmation_warning(result):
            # In this case the charge is outside of the user's authority
            if Permissions.add_extent_anywhere in g.session.user.permissions:
                # If the user has permission to add a charge anywhere, give them update permission without asking
                g.session.other_authority_update_permission = True
                g.session.commit()

            if not g.session.other_authority_update_permission:
                # if the user has not confirmed that they can edit charges outside of their authority, make them
                return redirect(url_for('modify_land_charge.get_update_location_confirmation'))

    return render_template(
        'modify_charge.html',
        charge_item=charge_item,
        updated=updated, updated_date=updated_date,
        charge_id=response.json()[0]['display_id'],
        geometry=json.dumps(charge_item.geometry),
        edited_fields=get_ordered_edited_fields(g.session.edited_fields, ReviewMap),
        map=ReviewMap
    )


@requires_permission([Permissions.vary_llc])
def clear_land_charge_changes(local_land_charge):
    g.session.add_charge_state = None
    g.session.edited_fields = []
    g.session.charge_added_outside_users_authority = None
    g.session.other_authority_update_permission = None
    g.session.other_authority_cancel_permission = None
    g.session.commit()
    current_app.logger.info("Charge cleared from session")
    return redirect(url_for('modify_land_charge.modify_land_charge', local_land_charge=local_land_charge))


@requires_permission([Permissions.vary_llc])
def modify_land_charge_confirm():
    current_app.logger.info("Endpoint called - Updating charge")
    AuditAPIService.audit_event(
        "Vary request submitted.",
        supporting_info={'id': calc_display_id(g.session.add_charge_state.local_land_charge)}
    )
    if g.session.charge_added_outside_users_authority:
        AuditAPIService.audit_event("Charge location varied, extent(s) modified to be outside users authority.",
                                    supporting_info={
                                        'originating-authority': g.session.user.organisation,
                                        'id': calc_display_id(g.session.add_charge_state.local_land_charge)})
    if g.session.other_authority_update_permission:
        AuditAPIService.audit_event("Charge location varied, extent(s) modified on a charge outside users authority.",
                                    supporting_info={
                                        'originating-authority': g.session.user.organisation,
                                        'id': calc_display_id(g.session.add_charge_state.local_land_charge)})
    MaintainApiService.update_charge(g.session.add_charge_state)
    charge_id = calc_display_id(g.session.add_charge_state.local_land_charge)
    g.session.add_charge_state = None
    g.session.edited_fields = None
    g.session.charge_added_outside_users_authority = None
    g.session.other_authority_update_permission = None
    g.session.other_authority_cancel_permission = None
    g.session.commit()
    current_app.logger.info("Charge removed from session - Rendering Template")
    return render_template('modify_confirmation.html', charge_id=charge_id)


def should_show_confirmation_warning(result):
    if Permissions.add_extent_england in g.session.user.permissions:
        return len(result) == 0
    else:
        return len(result) != 1 or g.session.user.organisation not in result
