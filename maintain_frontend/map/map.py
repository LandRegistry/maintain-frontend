from flask import Blueprint, current_app, request, Response
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.dependencies.local_authority_api.local_authority_api_service import LocalAuthorityService
import json

# Register Blueprint - Registered in blueprints.py with /map prefix so routes are relative
map_bp = Blueprint('map', __name__, static_folder='static', static_url_path='/static/map', template_folder='templates')


# AJAX local authority boundary lookup
@map_bp.route('/_authorities/<authority>/boundingbox', methods=['GET'])
def local_authority_service_boundingbox(authority):
    current_app.logger.info("Local Authority bounding box requested")
    if not request.is_xhr:
        current_app.logger.error("Request not xhr")
        raise ApplicationError(500)

    local_authority_service = LocalAuthorityService(current_app.config)
    response = local_authority_service.get_bounding_box(authority)
    return Response(json.dumps(response.json())), response.status_code, {"Content-Type": "application/json"}
