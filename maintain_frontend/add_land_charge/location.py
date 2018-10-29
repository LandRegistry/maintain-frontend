import json
from flask import g, redirect, url_for, render_template, request, current_app
from maintain_frontend.add_land_charge.validation.location_validator import AddLocationMapValidator
from maintain_frontend.decorators import requires_permission, requires_add_charge_session
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.add_land_charge.routing.review_router import ReviewRouter
from maintain_frontend.dependencies.local_authority_api.local_authority_api_service import LocalAuthorityService
from maintain_frontend.services.build_extents_from_features import build_extents_from_features
from maintain_frontend.services.address_converter import AddressConverter


def register_routes(bp):
    bp.add_url_rule('/add-local-land-charge/add-postcode', view_func=get_location, methods=['GET'])
    bp.add_url_rule('/add-local-land-charge/add-postcode', view_func=post_location, methods=['POST'])


@requires_permission([Permissions.add_llc])
@requires_add_charge_session()
def get_location():
    current_app.logger.info('Endpoint called')

    g.session.charge_added_outside_users_authority = False
    g.session.commit()

    if g.session.add_charge_state.geometry is not None:
        current_app.logger.info("Displaying page 'location.html' with pre-populated geometry")
        return render_template('location.html',
                               information=g.session.add_charge_state.geometry,
                               submit_url=url_for('add_land_charge.post_location'))

    current_app.logger.info("Displaying page 'location.html'")
    return render_template('location.html',
                           submit_url=url_for('add_land_charge.post_location'))


@requires_permission([Permissions.add_llc])
@requires_add_charge_session()
def post_location():
    current_app.logger.info('Endpoint called')

    features = None
    selected_address = None

    if request.form.get('saved-features'):
        features = json.loads(request.form['saved-features'].strip())

    if request.form.get('selected-address'):
        selected_address = json.loads(request.form['selected-address'])

    current_app.logger.info('Running validation')
    validation_errors = AddLocationMapValidator.validate(features)

    if validation_errors.errors:
        current_app.logger.warning('Validation errors occurred')
        return render_template(
            'location.html',
            validation_errors=validation_errors.errors,
            validation_summary_heading=validation_errors.summary_heading_text,
            information=features,
            submit_url=url_for('add_land_charge.post_location')
        ), 400

    current_app.logger.info('Updating session object')
    ReviewRouter.update_edited_field('geometry', features)

    select_address_param = False
    add_extent_anywhere_redirect_url = 'add_land_charge.get_address_for_charge'

    if selected_address and select_address_valid(selected_address):
        g.session.previously_selected_address = selected_address
        select_address_param = True
        add_extent_anywhere_redirect_url = 'add_land_charge.get_address_confirmation'

    g.session.add_charge_state.geometry = features
    g.session.commit()

    if Permissions.add_extent_anywhere not in g.session.user.permissions:
        extent = build_extents_from_features(features)
        result = LocalAuthorityService(current_app.config).get_authorities_by_extent(extent)

        if should_show_confirmation_warning(result):
            return redirect(url_for('add_land_charge.get_location_confirmation',
                                    address_selected=select_address_param))

    return redirect(ReviewRouter.get_redirect_url(add_extent_anywhere_redirect_url))


def should_show_confirmation_warning(result):
    if Permissions.add_extent_england in g.session.user.permissions:
        return len(result) == 0
    else:
        return len(result) != 1 or g.session.user.organisation not in result


def select_address_valid(address):
    try:
        AddressConverter.to_charge_address(address)
        return True
    except Exception:
        current_app.logger.info('selected address is not in a valid format. Address: {0}'.format(address))
        return False
