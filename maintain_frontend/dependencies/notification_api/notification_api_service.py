import json
from flask import current_app, g
from maintain_frontend import config
from maintain_frontend.exceptions import ApplicationError


class NotificationAPIService(object):

    @staticmethod
    def send_message_notify(email_address, template_id, personalisation):
        request_body = {
            "email_address": email_address,
            "template_id": template_id,
            "personalisation": personalisation,
            "reference": None
        }

        response = g.requests.post(
            config.NOTIFICATION_API_URL + '/v1/notifications',
            data=json.dumps(request_body),
            headers={"Content-Type": "application/json", "Accept": "application/json"}
        )

        if response.status_code != 201:
            raise ApplicationError()

        current_app.logger.info("Email message sent. Template ID: '{}'".format(template_id))
