from flask import current_app, g
from maintain_frontend.config import MAINTAIN_API_URL
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.dependencies.audit_api.audit_api import AuditAPIService
from maintain_frontend.dependencies.session_api.last_created_charge import LastCreatedCharge
from maintain_frontend.services.charge_id_services import calc_display_id
from datetime import datetime


class MaintainApiService(object):

    @staticmethod
    def add_charge(add_land_charge):
        current_app.logger.info("Attempting to add a charge")
        try:
            # Add Author Information
            add_land_charge.author = g.session.user.get_author_info()
            charge_json = add_land_charge.to_json()
            headers = {'Content-Type': 'application/json', 'X-Trace-ID': g.trace_id}

            current_app.logger.info("Posting to maintain-api/local-land-charge")
            response = g.requests.post(
                '{}/local-land-charge'.format(MAINTAIN_API_URL),
                json=charge_json,
                headers=headers
            )
        except Exception as ex:
            error_message = 'Failed to send land charge to maintain-api. ' \
                            'TraceID : {} - Exception - {}' \
                .format(g.trace_id, ex)
            current_app.logger.exception(error_message)
            AuditAPIService.audit_event("Failed to send land charge to maintain-api")
            raise ApplicationError(500)

        if response.status_code != 202:
            current_app.logger.exception(
                'Failed to send land charge to maintain-api. '
                'TraceID : {} - Status: {}, Message: {}'
                .format(g.trace_id, response.status_code, response.text)
            )
            AuditAPIService.audit_event("Failed to send land charge to maintain-api")
            raise ApplicationError(500)

        result = response.json()

        current_app.logger.info(
            "User ID '{}' created charge {}. Entry number: {}, registration date: {}.  TraceID={}".format(
                g.session.user.id,
                result['land_charge_id'],
                result['entry_number'],
                result['registration_date'],
                g.trace_id)
        )

        last_charge = LastCreatedCharge()
        last_charge.charge_id = result['land_charge_id']
        last_charge.entry_number = result['entry_number']
        last_charge.registration_date = datetime.strptime(result['registration_date'], "%Y-%m-%d").strftime("%d/%m/%Y")
        g.session.last_created_charge = last_charge
        g.session.commit()

    @staticmethod
    def update_charge(land_charge):
        current_app.logger.info("Attempting to update a charge")
        try:
            # Update Author Information
            land_charge.author = g.session.user.get_author_info()
            charge_json = land_charge.to_json()
            headers = {'Content-Type': 'application/json', 'X-Trace-ID': g.trace_id}

            current_app.logger.info(
                "Putting to maintain-api/local-land-charge/{}".format(charge_json['local-land-charge'])
            )
            response = g.requests.put(
                '{}/local-land-charge/{}'.format(MAINTAIN_API_URL, charge_json['local-land-charge']), json=charge_json,
                headers=headers)
        except Exception as ex:
            error_message = 'Failed to send land charge to maintain-api. ' \
                            'TraceID : {} - Exception - {}' \
                .format(g.trace_id, ex)
            current_app.logger.exception(error_message)
            AuditAPIService.audit_event("Failed to send land charge to maintain-api",
                                        supporting_info={'id': calc_display_id(land_charge.local_land_charge)})
            raise ApplicationError(500)

        if response.status_code != 202:
            current_app.logger.exception(
                'Failed to send land charge to maintain-api. '
                'TraceID : {} - Status: {}, Message: {}'
                .format(g.trace_id, response.status_code, response.text)
            )
            AuditAPIService.audit_event("Failed to send land charge to maintain-api",
                                        supporting_info={'id': calc_display_id(land_charge.local_land_charge)})
            raise ApplicationError(500)

        result = response.json()

        current_app.logger.info(
            "User ID '{}' updated charge {}. Entry number: {}, registration date: {}.  TraceID={}".format(
                g.session.user.id,
                result['land_charge_id'],
                result['entry_number'],
                result['registration_date'],
                g.trace_id)
        )

        last_charge = LastCreatedCharge()
        last_charge.charge_id = result['land_charge_id']
        last_charge.entry_number = result['entry_number']
        last_charge.registration_date = datetime.strptime(result['registration_date'], "%Y-%m-%d").strftime("%d/%m/%Y")
        g.session.last_created_charge = last_charge
        g.session.commit()
