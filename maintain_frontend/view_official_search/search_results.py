from flask import redirect, url_for, g, current_app, render_template
from datetime import datetime
from maintain_frontend.decorators import requires_lr
from maintain_frontend.dependencies.storage_api.storage_api_service import StorageAPIService


def register_routes(bp):
    bp.add_url_rule('/search-results', view_func=get_search_results, methods=['GET'])


@requires_lr()
def get_search_results():
    current_app.logger.info('Endpoint called')
    if g.session.search_details is None:
        current_app.logger.info('Redirecting to: %s', url_for("view_official_search.new"))
        return redirect(url_for("view_official_search.new"))

    if g.session.search_details.search_lapsed or g.session.search_details.parent_lapsed:
        # Either the search or the parent of a child search has lapsed beyond 6 months, so show error screen
        current_app.logger.info("Displaying page 'search_lapsed.html")
        return render_template('search_lapsed.html',
                               parent_lapsed=g.session.search_details.parent_lapsed,
                               reference=format_reference(g.session.search_details.search_reference),
                               search_date=format_date(g.session.search_details.search_date))
    else:
        # Show download page
        current_app.logger.info("Displaying page 'download_search.html")
        storage_api_service = StorageAPIService(current_app.config)
        pdf_link = storage_api_service.get_external_url_for_document_url(g.session.search_details.pdf_link)

        return render_template('download_search.html',
                               area_description=g.session.search_details.area_description,
                               reference=format_reference(g.session.search_details.search_reference),
                               pdf_link=pdf_link)


def format_reference(reference):
    # format search reference for display
    f = '%09d' % int(reference)
    formatted_ref = "{} {} {}".format(f[:3], f[3:6], f[6:])
    return formatted_ref


def format_date(date):
    # format date for display
    day_number = datetime.strftime(date, "%-d")[-1:]
    suffix = 'th'
    if day_number == '1':
        suffix = 'st'
    elif day_number == '2':
        suffix = 'nd'
    elif day_number == '3':
        suffix = 'rd'

    display_date = '{}{} {} {}'.format(datetime.strftime(date, "%-d"),
                                       suffix,
                                       datetime.strftime(date, "%B"),
                                       datetime.strftime(date, "%Y"))
    return display_date
