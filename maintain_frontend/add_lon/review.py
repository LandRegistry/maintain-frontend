import json
from flask import g, redirect, url_for, render_template, current_app, request
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.dependencies.audit_api.audit_api import AuditAPIService
from maintain_frontend.dependencies.maintain_api.maintain_api_service import MaintainApiService
from maintain_frontend.add_lon.enumerations.review_map import ReviewMap


def register_routes(bp):
    bp.add_url_rule('/add-light-obstruction-notice/check-your-answers', view_func=get_review, methods=['GET'])
    bp.add_url_rule('/add-light-obstruction-notice/check-your-answers', view_func=post_review, methods=['POST'])


@requires_permission([Permissions.add_lon])
def get_review():
    current_app.logger.info('Endpoint called')

    if g.session.add_lon_charge_state is None:
        current_app.logger.info('Redirecting to: {}'.format(url_for('add_lon.new')))
        return redirect(url_for('add_lon.new'))

    g.session.redirect_route = 'add_lon.get_review'
    g.session.commit()

    return render_template('review_lon.html',
                           add_lon_charge_state=g.session.add_lon_charge_state,
                           filenames=g.session.filenames,
                           edited_fields=g.session.edited_fields,
                           geometry=json.dumps(g.session.add_lon_charge_state.geometry),
                           map=ReviewMap)


@requires_permission([Permissions.add_lon])
def post_review():
    current_app.logger.info('Endpoint called')

    g.session.redirect_route = None
    g.session.edited_fields = {}
    g.session.commit()

    if g.session.add_lon_charge_state is None:
        current_app.logger.info('Redirecting to: {}'.format(url_for('add_lon.new')))
        return redirect(url_for('add_lon.new'))

    redirect_url = url_for('add_lon.get_confirmation')
    current_app.logger.info('Redirecting to next step: {}'.format(redirect_url))

    submit_token = request.form.get('csrf_token')

    if submit_token != g.session.submit_token:
        g.session.submit_token = submit_token
        g.session.commit()
        AuditAPIService.audit_event("Submitting the charge", supporting_info=g.session.add_lon_charge_state.to_json())
        MaintainApiService.add_charge(g.session.add_lon_charge_state)
        AuditAPIService.audit_event("Charge created", supporting_info={'id': g.session.last_created_charge.charge_id})

    # Audit the LON payment method
    '''if g.session.payment_info.payment_method == 'govuk':
        AuditAPIService.audit_event("Payment made via GOV.UK Pay",
                                    supporting_info={'reference': g.session.payment_info.payment_ref,
                                                     'charge_id': g.session.last_created_charge.charge_id})
    elif g.session.payment_info.payment_method == 'cheque':
        AuditAPIService.audit_event("Payment made by cheque",
                                    supporting_info={'charge_id': g.session.last_created_charge.charge_id}
                                    )
    else:
        AuditAPIService.audit_event("No payment needed",
                                    supporting_info={'explanation': g.session.payment_info.no_payment_notes,
                                                     'charge_id': g.session.last_created_charge.charge_id})'''

    return redirect(redirect_url)
