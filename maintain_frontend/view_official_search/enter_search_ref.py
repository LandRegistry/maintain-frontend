from flask import redirect, url_for, g, current_app, render_template, request
from maintain_frontend.decorators import requires_lr
from maintain_frontend.view_official_search.validation.search_reference_validator import SearchReferenceValidator
from maintain_frontend.dependencies.search_local_land_charge_api.search_llc_api_service import SearchLLCAPIService
from maintain_frontend.exceptions import ApplicationError
from datetime import datetime


def register_routes(bp):
    bp.add_url_rule('/enter-search-ref', view_func=get_enter_search_ref, methods=['GET'])
    bp.add_url_rule('/enter-search-ref', view_func=post_enter_search_ref, methods=['POST'])


@requires_lr()
def get_enter_search_ref():
    current_app.logger.info('Endpoint called')
    if g.session.search_details is None:
        current_app.logger.info('Redirecting to: %s', url_for("view_official_search.new"))
        return redirect(url_for("view_official_search.new"))

    previous_data = None

    # If search reference has already been set then populate for edit
    if g.session.search_details is not None:
        current_app.logger.info("Search reference has been found, populating for edit")
        previous_data = g.session.search_details.search_reference

    current_app.logger.info("Displaying page 'enter_search_ref.html")
    return render_template('enter_search_ref.html',
                           request_body=previous_data,
                           submit_url=url_for("view_official_search.post_enter_search_ref"))


@requires_lr()
def post_enter_search_ref():
    search_reference = request.form.get('search_reference')
    # Strip spaces and convert to int if possible to remove leading zeros
    try:
        search_reference = str(int(search_reference.replace(' ', '')))
    except Exception as e:
        pass

    current_app.logger.info("Endpoint called with search_reference as '{}'".format(search_reference))

    validator = SearchReferenceValidator.validate(search_reference)
    if validator.errors:
        current_app.logger.warning("Validation errors found")
        return render_template(
            'enter_search_ref.html',
            validation_errors=validator.errors,
            validation_summary_heading=validator.summary_heading_text,
            error_heading_message=validator.summary_heading_text,
            request_body=request.form,
            submit_url=url_for("view_official_search.post_enter_search_ref")
        ), 400

    search_results = get_search(search_reference)
    search_lapsed = False
    parent_lapsed = False
    if search_results is None:
        # No search results so return to the page with an error stating such
        validator = SearchReferenceValidator.validate(search_reference, found=False)
        current_app.logger.warning("Validation errors found")
        return render_template(
            'enter_search_ref.html',
            validation_errors=validator.errors,
            validation_summary_heading=validator.summary_heading_text,
            error_heading_message=validator.summary_heading_text,
            request_body=request.form,
            submit_url=url_for("view_official_search.post_enter_search_ref")
        ), 400

    elif 'parent-search-id' in search_results:
        # If the search is a child, get the parent results to check if it is expired
        parent_search_results = get_search(search_results['parent-search-id'])
        if parent_search_results is None:
            # Although unlikely, it may possibly happen that the child search exists but for some reason the parent
            # does not, in this case return to the search screen with an error
            validator = SearchReferenceValidator.validate(search_reference, found=False)
            current_app.logger.warning("Validation errors found")
            return render_template(
                'enter_search_ref.html',
                validation_errors=validator.errors,
                validation_summary_heading=validator.summary_heading_text,
                error_heading_message=validator.summary_heading_text,
                request_body=request.form,
                submit_url=url_for("view_official_search.post_enter_search_ref")
            ), 400
        else:
            # Get the date of the parent search and check if it lapsed (i.e. more than 6 months old)
            search_date = parent_search_results['search-date']
            if parent_search_results['lapsed-date']:
                parent_lapsed = True
                search_reference = parent_search_results['search-id']

    else:
        # Get the date of the search and check if it lapsed (i.e. more than 6 months old)
        search_date = search_results['search-date']
        if search_results['lapsed-date']:
            search_lapsed = True

    g.session.search_details.search_reference = search_reference
    g.session.search_details.search_date = datetime.strptime(search_date, '%Y-%m-%dT%H:%M:%S+00:00')
    g.session.search_details.search_lapsed = search_lapsed
    g.session.search_details.parent_lapsed = parent_lapsed
    g.session.search_details.area_description = search_results['search-area-description']
    g.session.search_details.pdf_link = search_results['document-url']
    g.session.commit()

    return redirect(url_for("view_official_search.get_search_results"))


def get_search(search_reference):
    response = SearchLLCAPIService.get_by_reference_number(search_reference)

    if response.status_code == 404:
        return None
    elif response.status_code == 500:
        current_app.logger.error("Search service error - Returning error")
        raise ApplicationError(500)

    current_app.logger.info("Search results found for ID {}".format(search_reference))
    return response.json()
