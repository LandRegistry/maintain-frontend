from flask import render_template, redirect, url_for, request, current_app, g
from maintain_frontend.add_land_charge.validation.land_compensation_land_sold_validator import \
    LandCompensationLandSoldValidator
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.add_land_charge.routing.review_router import ReviewRouter


def register_routes(bp):
    bp.add_url_rule('/add-local-land-charge/land-sold-to-authority',
                    view_func=get_land_compensation_land_sold, methods=['GET'])
    bp.add_url_rule('/add-local-land-charge/land-sold-to-authority',
                    view_func=post_land_compensation_land_sold, methods=['POST'])


@requires_permission([Permissions.add_llc])
def get_land_compensation_land_sold():
    current_app.logger.info('Endpoint called')
    if g.session.add_charge_state is None:
        current_app.logger.info('Redirecting to: {}'.format(url_for('add_land_charge.new')))
        return redirect(url_for('add_land_charge.new'))

    request_body = {
        'land-sold-description': g.session.add_charge_state.land_sold_description,
        'land-works-particulars': g.session.add_charge_state.land_works_particulars
    }

    current_app.logger.info("Displaying page 'land_compensation_land_sold.html'")
    return render_template('land_compensation_land_sold.html',
                           request_body=request_body,
                           submit_url=url_for('add_land_charge.post_land_compensation_land_sold'))


@requires_permission([Permissions.add_llc])
def post_land_compensation_land_sold():
    current_app.logger.info("Endpoint called with land-sold-description = '%s' and land-works-particulars = '%s'",
                            request.form.get('land-sold-description', ''),
                            request.form.get('land-works-particulars', ''))

    if g.session.add_charge_state is None:
        current_app.logger.info('Redirecting to: {}'.format(url_for('add_land_charge.new')))
        return redirect(url_for('add_land_charge.new'))

    description = request.form['land-sold-description'].strip()
    land_works_particulars = request.form['land-works-particulars'].strip()

    current_app.logger.info('Running validation')
    validation_errors = LandCompensationLandSoldValidator.validate(description, land_works_particulars)

    if validation_errors.errors:
        current_app.logger.warning('Validation errors occurred')
        return render_template('land_compensation_land_sold.html',
                               validation_errors=validation_errors.errors,
                               validation_summary_heading=validation_errors.summary_heading_text,
                               request_body=request.form,
                               submit_url=url_for('add_land_charge.post_land_compensation_land_sold')), 400

    current_app.logger.info('Updating session object')
    ReviewRouter.update_edited_field('land_sold_description', description)
    g.session.add_charge_state.land_sold_description = description

    ReviewRouter.update_edited_field('land_works_particulars', land_works_particulars)
    g.session.add_charge_state.land_works_particulars = land_works_particulars

    g.session.commit()

    return redirect(ReviewRouter.get_redirect_url('add_land_charge.get_charge_date'))
