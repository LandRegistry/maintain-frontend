from flask import render_template, redirect, url_for, request, g, current_app
from maintain_frontend.add_land_charge.validation.charge_date_validator import ChargeDateValidator
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from datetime import date
from maintain_frontend.add_land_charge.routing.review_router import ReviewRouter


def register_routes(bp):
    bp.add_url_rule('/add-local-land-charge/when-was-charge-created', view_func=get_charge_date, methods=['GET'])
    bp.add_url_rule('/add-local-land-charge/when-was-charge-created', view_func=post_charge_date, methods=['POST'])


@requires_permission([Permissions.add_llc])
def get_charge_date():
    current_app.logger.info('Endpoint called')

    if g.session.add_charge_state is None:
        current_app.logger.info('Redirecting to: {}'.format(url_for('add_land_charge.new')))
        return redirect(url_for('add_land_charge.new'))

    create_date = g.session.add_charge_state.charge_creation_date
    charge_date = None
    if create_date:
        charge_date = {
            'day': str(create_date.day),
            'month': str(create_date.month),
            'year': str(create_date.year)
        }

    current_app.logger.info("Displaying page 'charge_date.html'")
    return render_template('charge_date.html',
                           submit_url=url_for('add_land_charge.post_charge_date'),
                           date=charge_date)


@requires_permission([Permissions.add_llc])
def post_charge_date():
    current_app.logger.info("Endpoint called with date-day = '{}', date-month = '{}', date-year = '{}'".format(
                            request.form.get('date-day', ''),
                            request.form.get('date-month', ''),
                            request.form.get('date-year', '')))

    if g.session.add_charge_state is None:
        current_app.logger.info('Redirecting to: {}'.format(url_for('add_land_charge.new')))
        return redirect(url_for('add_land_charge.new'))

    day = request.form.get('date-day')
    month = request.form.get('date-month')
    year = request.form.get('date-year')

    current_app.logger.info('Running validation')
    validation_errors = ChargeDateValidator.validate(day, month, year)
    if validation_errors.errors:
        charge_date = {
            'day': day,
            'month': month,
            'year': year
        }
        current_app.logger.warning('Validation errors occurred')
        return render_template('charge_date.html',
                               validation_errors=validation_errors.errors,
                               validation_summary_heading=validation_errors.summary_heading_text,
                               submit_url=url_for('add_land_charge.post_charge_date'),
                               request=request,
                               date=charge_date)

    if year and month and day:
        current_app.logger.info('Updating session object')
        charge_creation_date = date(int(year), int(month), int(day))

        ReviewRouter.update_edited_field('charge_creation_date', charge_creation_date)
        g.session.add_charge_state.charge_creation_date = charge_creation_date
        g.session.commit()

    return redirect(ReviewRouter.get_redirect_url('add_land_charge.get_location'))
