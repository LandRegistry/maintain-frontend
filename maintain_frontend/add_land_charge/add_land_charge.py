from flask import redirect, url_for, g, current_app
from maintain_frontend.models import LocalLandChargeItem
from maintain_frontend.config import SCHEMA_VERSION


def register_routes(bp):
    bp.add_url_rule('/add-local-land-charge', view_func=new, methods=['GET'])
    bp.add_url_rule('/add-local-land-charge-behalf',
                    view_func=new_behalf_of_authority, methods=['GET'])


def new():
    """This will setup state for adding a new land charge and redirect to the starting page."""
    g.session.add_charge_state = LocalLandChargeItem()
    g.session.redirect_route = None
    g.session.edited_fields = []
    g.session.add_charge_state.originating_authority = g.session.user.organisation
    g.session.add_charge_state.schema_version = SCHEMA_VERSION
    g.session.adding_charge_for_other_authority = False
    g.session.upload_shapefile_processed = None
    g.session.category_details = None
    g.session.category_confirmation = None
    g.session.charge_added_outside_users_authority = None
    g.session.other_authority_update_permission = None
    g.session.other_authority_cancel_permission = None
    g.session.commit()

    current_app.logger.info('Created new session object: {}'.format(
        g.session.add_charge_state.to_json()))
    current_app.logger.info('Redirecting to: {}'.format(
        url_for('add_land_charge.get_charge_type')))
    return redirect(url_for('add_land_charge.get_charge_type'))


def new_behalf_of_authority():
    """This will setup state for adding a new land charge and redirect to the starting page."""
    g.session.add_charge_state = LocalLandChargeItem()
    g.session.redirect_route = None
    g.session.edited_fields = []
    g.session.add_charge_state.statutory_provision = 'Not provided'
    g.session.adding_charge_for_other_authority = True
    g.session.upload_shapefile_processed = None
    g.session.category_details = None
    g.session.category_confirmation = None
    g.session.add_charge_state.schema_version = SCHEMA_VERSION
    g.session.charge_added_outside_users_authority = None
    g.session.other_authority_update_permission = None
    g.session.other_authority_cancel_permission = None
    g.session.commit()

    current_app.logger.info('Created new session object: {}'.format(
        g.session.add_charge_state.to_json()))
    current_app.logger.info('Redirecting to: {}'.format(
        url_for('add_land_charge.get_originating_authority_page')))

    return redirect(url_for('add_land_charge.get_originating_authority_page'))
