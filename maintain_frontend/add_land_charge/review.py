import json
from flask import g, redirect, url_for, render_template, current_app, request
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.dependencies.audit_api.audit_api import AuditAPIService
from maintain_frontend.dependencies.maintain_api.maintain_api_service import MaintainApiService
from maintain_frontend.add_land_charge.enumerations.review_map import ReviewMap
from maintain_frontend.services.field_utilities import get_ordered_edited_fields


def register_routes(bp):
    bp.add_url_rule('/add-local-land-charge/check-your-answers', view_func=get_review, methods=['GET'])
    bp.add_url_rule('/add-local-land-charge/check-your-answers', view_func=post_review, methods=['POST'])


@requires_permission([Permissions.add_llc])
def get_review():
    current_app.logger.info('Endpoint called')

    if g.session.add_charge_state is None:
        current_app.logger.info('Redirecting to: {}'.format(url_for('add_land_charge.new')))
        return redirect(url_for('add_land_charge.new'))

    g.session.redirect_route = 'add_land_charge.get_review'
    g.session.commit()

    return render_template('review.html',
                           add_charge_state=g.session.add_charge_state,
                           edited_fields=get_ordered_edited_fields(g.session.edited_fields, ReviewMap),
                           geometry=json.dumps(g.session.add_charge_state.geometry),
                           map=ReviewMap)


@requires_permission([Permissions.add_llc])
def post_review():
    current_app.logger.info('Endpoint called')

    g.session.redirect_route = None
    g.session.edited_fields = []
    g.session.commit()

    if g.session.add_charge_state is None:
        current_app.logger.info('Redirecting to: {}'.format(url_for('add_land_charge.new')))
        return redirect(url_for('add_land_charge.new'))

    redirect_url = url_for('add_land_charge.get_confirmation')
    current_app.logger.info('Redirecting to next step: {}'.format(redirect_url))

    submit_token = request.form.get('csrf_token')

    if submit_token != g.session.submit_token:
        g.session.submit_token = submit_token
        g.session.commit()

        added_outside_users_authority = g.session.charge_added_outside_users_authority

        if added_outside_users_authority:
            g.session.charge_added_outside_users_authority = None
            g.session.commit()

        AuditAPIService.audit_event("Submitting the charge", supporting_info=g.session.add_charge_state.to_json())
        MaintainApiService.add_charge(g.session.add_charge_state)

        if added_outside_users_authority:
            AuditAPIService.audit_event("Charge added outside users authority.",
                                        supporting_info={'originating-authority': g.session.user.organisation,
                                                         'id': g.session.last_created_charge.charge_id})

        AuditAPIService.audit_event("Charge created",
                                    supporting_info={'id': g.session.last_created_charge.charge_id})

    return redirect(redirect_url)
