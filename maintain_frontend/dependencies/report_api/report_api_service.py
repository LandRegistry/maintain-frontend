from flask import current_app, g, Response
from maintain_frontend.config import REPORT_API_BASE_URL


class ReportAPIService(object):
    """Service class for making requests to report-api"""

    @staticmethod
    def send_number_of_charges_per_search_data(report_data):
        current_app.logger.info(
            "Calling the report data endpoint of the Report API "
            "with the following data: {}".format(report_data)
        )
        try:
            return g.requests.post(
                "{}/v1.0/number-of-charges-per-search".format(REPORT_API_BASE_URL),
                json=report_data,
                headers={'Content-Type': 'application/json'}
            )
        except Exception as ex:
            current_app.logger.error(
                "Call to report data endpoint of the Report API failed"
                " - Error {}".format(ex))
            return Response(response=ex, status=500)
