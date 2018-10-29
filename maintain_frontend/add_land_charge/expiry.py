from flask import g, render_template, request, redirect, url_for, current_app
from datetime import date
from maintain_frontend.add_land_charge.validation.expiry_validator import ExpiryValidator
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.add_land_charge.routing.review_router import ReviewRouter


def register_routes(bp):
    bp.add_url_rule('/add-local-land-charge/does-charge-expire', view_func=get_expiry, methods=['GET'])
    bp.add_url_rule('/add-local-land-charge/does-charge-expire', view_func=post_expiry, methods=['POST'])


@requires_permission([Permissions.add_llc])
def get_expiry():
    current_app.logger.info('Endpoint called')

    if g.session.add_charge_state is None:
        current_app.logger.info('Redirecting to: {}'.format(url_for('add_land_charge.new')))
        return redirect(url_for('add_land_charge.new'))

    request_body = {}
    if g.session.add_charge_state.expiry_date is not None:
        request_body['does_charge_expire'] = 'yes'
        request_body['charge_expiry_day'] = g.session.add_charge_state.expiry_date.day
        request_body['charge_expiry_month'] = g.session.add_charge_state.expiry_date.month
        request_body['charge_expiry_year'] = g.session.add_charge_state.expiry_date.year

    current_app.logger.info("Displaying page 'expiry.html'")
    return render_template('expiry.html',
                           request_body=request_body,
                           submit_url=url_for('add_land_charge.post_expiry'))


@requires_permission([Permissions.add_llc])
def post_expiry():
    current_app.logger.info("Endpoint called with does_charge_expire = '{}', charge_expiry_day = '{}', "
                            "charge_expiry_month = '{}', charge_expiry_year = '{}'".format(
                                request.form.get('does_charge_expire', ''),
                                request.form.get('charge_expiry_day', ''),
                                request.form.get('charge_expiry_month', ''),
                                request.form.get('charge_expiry_year', '')
                            ))

    if g.session.add_charge_state is None:
        current_app.logger.info('Redirecting to: {}'.format(url_for('add_land_charge.new')))
        return redirect(url_for('add_land_charge.new'))

    does_charge_expire = request.form.get('does_charge_expire', '')
    charge_expiry_day = request.form.get('charge_expiry_day', '')
    charge_expiry_month = request.form.get('charge_expiry_month', '')
    charge_expiry_year = request.form.get('charge_expiry_year', '')

    validation_errors = ExpiryValidator.validate(
        does_charge_expire,
        charge_expiry_day,
        charge_expiry_month,
        charge_expiry_year
    )

    current_app.logger.info('Running validation')
    if validation_errors.errors:
        current_app.logger.warning('Validation errors occurred')
        return render_template(
            'expiry.html',
            validation_errors=validation_errors.errors,
            validation_summary_heading=validation_errors.summary_heading_text,
            submit_url=url_for('add_land_charge.post_expiry'),
            request_body=request.form
        ), 400

    if does_charge_expire == 'yes':
        charge_expiry_date = None

        if (
            charge_expiry_day and
            charge_expiry_month and
            charge_expiry_year
        ):
            charge_expiry_date = date(
                int(charge_expiry_year),
                int(charge_expiry_month),
                int(charge_expiry_day)
            )

        current_app.logger.info('Update expiry_date in session object')
        ReviewRouter.update_edited_field('expiry_date', charge_expiry_date)

        g.session.add_charge_state.expiry_date = charge_expiry_date
        g.session.commit()
    else:
        g.session.add_charge_state.expiry_date = None
        g.session.commit()

    return redirect(ReviewRouter.get_redirect_url('add_land_charge.get_additional_info'))
