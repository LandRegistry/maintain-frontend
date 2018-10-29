from flask import Blueprint
import maintain_frontend.llc1.create_llc1
import maintain_frontend.llc1.search_location
import maintain_frontend.llc1.search_extent
import maintain_frontend.llc1.search_description
import maintain_frontend.llc1.search_result


create_llc1_bp = Blueprint('create_llc1', __name__,
                           static_url_path='/static/llc1',
                           static_folder='static',
                           template_folder='templates')

maintain_frontend.llc1.create_llc1.register_routes(create_llc1_bp)
maintain_frontend.llc1.search_location.register_routes(create_llc1_bp)
maintain_frontend.llc1.search_extent.register_routes(create_llc1_bp)
maintain_frontend.llc1.search_description.register_routes(create_llc1_bp)
maintain_frontend.llc1.search_result.register_routes(create_llc1_bp)
