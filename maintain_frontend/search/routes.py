from flask import Blueprint

import maintain_frontend.search.search
import maintain_frontend.search.search_by_reference

# Register Blueprint - Registered in blueprints.py
search_bp = Blueprint('search', __name__, static_folder='static', static_url_path='/static/search',
                      template_folder='templates')

maintain_frontend.search.search.register_routes(search_bp)
maintain_frontend.search.search_by_reference.register_routes(search_bp)
