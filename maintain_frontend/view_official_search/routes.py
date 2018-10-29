from flask import Blueprint

import maintain_frontend.view_official_search.view_official_search
import maintain_frontend.view_official_search.enter_search_ref
import maintain_frontend.view_official_search.search_results


# Blueprint Definition
view_official_search_bp = Blueprint('view_official_search', __name__,
                                    template_folder='templates')


maintain_frontend.view_official_search.view_official_search.register_routes(view_official_search_bp)
maintain_frontend.view_official_search.enter_search_ref.register_routes(view_official_search_bp)
maintain_frontend.view_official_search.search_results.register_routes(view_official_search_bp)
