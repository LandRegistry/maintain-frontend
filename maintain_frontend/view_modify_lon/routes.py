from flask import Blueprint
import maintain_frontend.view_modify_lon.cancel_lon
import maintain_frontend.view_modify_lon.view_lon
import maintain_frontend.view_modify_lon.modify_lon
import maintain_frontend.view_modify_lon.modify_lon_details
import maintain_frontend.view_modify_lon.edit_applicant_info
import maintain_frontend.view_modify_lon.edit_dominant_building
import maintain_frontend.view_modify_lon.edit_dominant_building_extent
import maintain_frontend.view_modify_lon.edit_servient_structure_height
import maintain_frontend.view_modify_lon.edit_servient_structure_position
import maintain_frontend.view_modify_lon.edit_lon_land_interest

cancel_lon_bp = Blueprint('cancel_lon', __name__,
                          static_folder='static', static_url_path='/static/view_modify_lon',
                          template_folder='templates', url_prefix='/cancel-light-obstruction-notice')

view_lon_bp = Blueprint('view_lon', __name__, static_folder='static',
                        static_url_path='/static/view_modify_lon',
                        template_folder='templates', url_prefix='/view-light-obstruction-notice')

modify_lon_bp = Blueprint('modify_lon', __name__, static_folder='static',
                          static_url_path='/static/view_modify_lon',
                          template_folder='templates', url_prefix='/update-light-obstruction-notice')

# Cancel
maintain_frontend.view_modify_lon.cancel_lon.register_routes(cancel_lon_bp)

# View
maintain_frontend.view_modify_lon.view_lon.register_routes(view_lon_bp)

# Modify
maintain_frontend.view_modify_lon.modify_lon.register_routes(modify_lon_bp)
maintain_frontend.view_modify_lon.modify_lon_details.register_routes(modify_lon_bp)
maintain_frontend.view_modify_lon.edit_applicant_info.register_routes(modify_lon_bp)
maintain_frontend.view_modify_lon.edit_dominant_building.register_routes(modify_lon_bp)
maintain_frontend.view_modify_lon.edit_dominant_building_extent.register_routes(modify_lon_bp)
maintain_frontend.view_modify_lon.edit_servient_structure_height.register_routes(modify_lon_bp)
maintain_frontend.view_modify_lon.edit_servient_structure_position.register_routes(modify_lon_bp)
maintain_frontend.view_modify_lon.edit_lon_land_interest.register_routes(modify_lon_bp)
