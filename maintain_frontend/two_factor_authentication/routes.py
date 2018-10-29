from flask import Blueprint
import maintain_frontend.two_factor_authentication.two_factor_authentication

two_factor_authentication_bp = Blueprint('two_factor_authentication', __name__, static_folder='static',
                                         static_url_path='/static/two_factor_authentication',
                                         template_folder='templates')

maintain_frontend.two_factor_authentication.two_factor_authentication.register_routes(two_factor_authentication_bp)
