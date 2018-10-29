from flask import render_template, redirect, url_for, request, current_app, g
from maintain_frontend.add_land_charge.validation.charge_description_validator import ChargeDescriptionValidator
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions
from maintain_frontend.add_land_charge.routing.review_router import ReviewRouter
from maintain_frontend.services.field_utilities import has_value_changed


def register_routes(bp):
    bp.add_url_rule('/add-local-land-charge/charge-description', view_func=get_charge_description, methods=['GET'])
    bp.add_url_rule('/add-local-land-charge/charge-description',
                    view_func=post_charge_description, methods=['POST'])


@requires_permission([Permissions.add_llc])
def get_charge_description():
    current_app.logger.info('Endpoint called')

    try:
        if g.session.add_charge_state is None:
            current_app.logger.info('Redirecting to: {}'.format(url_for('add_land_charge.new')))
            return redirect(url_for('add_land_charge.new'))

        current_app.logger.info("Displaying page 'charge_description.html'")
        return render_template('charge_description.html',
                               data=g.session.add_charge_state.supplementary_information,
                               submit_url=url_for('add_land_charge.post_charge_description'))

    except Exception as ex:
        error_message = 'Failed getting add_land_charge description page. ' \
                        'TraceID: {} - Exception - {}' \
            .format(g.trace_id, ex)

        current_app.logger.error(error_message)
        raise ApplicationError(error_message)


@requires_permission([Permissions.add_llc])
def post_charge_description():
    current_app.logger.info("Endpoint called with charge-description = '{}'".format(
        request.form.get('charge-description', '').strip()
    ))

    if g.session.add_charge_state is None:
        current_app.logger.info('Redirecting to: {}'.format(url_for('add_land_charge.new')))
        return redirect(url_for('add_land_charge.new'))

    description = request.form['charge-description'].strip()

    current_app.logger.info('Running validation')
    validation_errors = ChargeDescriptionValidator.validate(description)

    if validation_errors.errors:
        current_app.logger.warning('Validation errors occurred')
        return render_template('charge_description.html',
                               validation_errors=validation_errors.errors,
                               validation_summary_heading=validation_errors.summary_heading_text,
                               data=description,
                               submit_url=url_for('add_land_charge.post_charge_description')), 400

    current_app.logger.info('Updating session object')
    if has_value_changed(g.session.add_charge_state.supplementary_information, description):
        ReviewRouter.update_edited_field('supplementary_information', description)
        g.session.add_charge_state.supplementary_information = description
        g.session.commit()

    return redirect(ReviewRouter.get_redirect_url('add_land_charge.get_review'))
