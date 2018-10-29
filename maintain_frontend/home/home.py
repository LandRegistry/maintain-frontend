from flask import Blueprint, render_template, current_app

# Register Blueprint - Registered in blueprints.py
home_bp = Blueprint(
    'home', __name__, static_folder='static', static_url_path='/home/static', template_folder='templates'
)


@home_bp.route('/', methods=['GET'])
def get():
    current_app.logger.info("Endpoint called")
    return render_template('home.html')
