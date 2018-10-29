from maintain_frontend.config import AUDIT_API_URL
from maintain_frontend.exceptions import ApplicationError
from flask import current_app, g
from datetime import datetime, timezone
import json
import socket
import copy


class AuditAPIService(object):
    @staticmethod
    def audit_event(activity, origin_id=None, component_name="maintain-frontend",
                    business_service="LLC Maintain Frontend", trace_id=None, supporting_info=None):
        """Sends audit event to Audit API"""

        if not origin_id:
            if hasattr(g, 'session'):
                origin_id = g.session.user.id
            else:
                origin_id = "maintain-frontend"
        if not trace_id:
            trace_id = g.trace_id

        event = {'activity': activity,
                 'activity_timestamp': datetime.now(timezone.utc).isoformat(),
                 'origin_id': origin_id,
                 'component_name': component_name,
                 'business_service': business_service,
                 'trace_id': trace_id}

        host_ip = socket.gethostbyname(socket.gethostname())

        if supporting_info:
            extra_info = copy.copy(supporting_info)
            extra_info['machine_ip'] = host_ip
            event['supporting_info'] = extra_info
        else:
            supporting_info = {'machine_ip': host_ip}
            event['supporting_info'] = supporting_info

        try:
            current_app.logger.info("Sending event to audit api")
            response = g.requests.post('{}/records'.format(AUDIT_API_URL),
                                       data=json.dumps(event),
                                       headers={'Content-Type': 'application/json'})
        except Exception:
            current_app.logger.error("Error occurred performing audit")
            raise ApplicationError(500)

        if response.status_code != 201:
            raise ApplicationError(500)
