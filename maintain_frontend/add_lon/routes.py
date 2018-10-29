from flask import Blueprint

import maintain_frontend.add_lon.add_lon
import maintain_frontend.add_lon.confirmation
import maintain_frontend.add_lon.applicant_info
import maintain_frontend.add_lon.dominant_building
import maintain_frontend.add_lon.dominant_building_extent
import maintain_frontend.add_lon.lon_land_interest
import maintain_frontend.add_lon.payment_method
import maintain_frontend.add_lon.upload_lon_documents
import maintain_frontend.add_lon.servient_structure_height
import maintain_frontend.add_lon.servient_structure_position
import maintain_frontend.add_lon.review


# Blueprint Definition
add_lon_bp = Blueprint('add_lon', __name__,
                       static_url_path='/static/add-light-obstruction-notice',
                       static_folder='static',
                       template_folder='templates')

maintain_frontend.add_lon.add_lon.register_routes(add_lon_bp)
maintain_frontend.add_lon.confirmation.register_routes(add_lon_bp)
maintain_frontend.add_lon.dominant_building.register_routes(add_lon_bp)
maintain_frontend.add_lon.applicant_info.register_routes(add_lon_bp)
maintain_frontend.add_lon.dominant_building_extent.register_routes(add_lon_bp)
maintain_frontend.add_lon.lon_land_interest.register_routes(add_lon_bp)
maintain_frontend.add_lon.payment_method.register_routes(add_lon_bp)
maintain_frontend.add_lon.upload_lon_documents.register_routes(add_lon_bp)
maintain_frontend.add_lon.servient_structure_height.register_routes(add_lon_bp)
maintain_frontend.add_lon.servient_structure_position.register_routes(add_lon_bp)
maintain_frontend.add_lon.review.register_routes(add_lon_bp)
