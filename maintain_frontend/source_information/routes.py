from flask import Blueprint
import maintain_frontend.source_information.source_information
import maintain_frontend.source_information.add_source_information
import maintain_frontend.source_information.update_source_information
import maintain_frontend.source_information.delete_source_information

# Register Blueprint - Registered in blueprints.py
source_info_bp = Blueprint('source_info', __name__, static_folder='static', static_url_path='/static/source_info',
                           template_folder='templates')

maintain_frontend.source_information.source_information.register_routes(source_info_bp)
maintain_frontend.source_information.add_source_information.register_routes(source_info_bp)
maintain_frontend.source_information.update_source_information.register_routes(source_info_bp)
maintain_frontend.source_information.delete_source_information.register_routes(source_info_bp)
