# Import every blueprint file
from maintain_frontend import general
# Common Map
from maintain_frontend.map.map import map_bp
# Home
from maintain_frontend.home.home import home_bp
# Search
from maintain_frontend.search.routes import search_bp
# Add Land Charge
from maintain_frontend.add_land_charge.routes import add_land_charge_bp
# View Land Charge
from maintain_frontend.view_modify_land_charge.routes import view_llc_bp
# Modify Land Charge
from maintain_frontend.view_modify_land_charge.routes import modify_land_charge_bp
# Cancel Land Charge
from maintain_frontend.view_modify_land_charge.routes import cancel_land_charge_bp
# Create LLC1
from maintain_frontend.llc1.routes import create_llc1_bp
# Add LON
from maintain_frontend.add_lon.routes import add_lon_bp
# Address finder
from maintain_frontend.address_finder.address_finder import address_finder_bp
# View LON
from maintain_frontend.view_modify_lon.routes import view_lon_bp
# Modify LON
from maintain_frontend.view_modify_lon.routes import modify_lon_bp
# Cancel LON
from maintain_frontend.view_modify_lon.routes import cancel_lon_bp
# Reports
from maintain_frontend.reports.report_downloader import reports_bp
# Source Information
from maintain_frontend.source_information.routes import source_info_bp
# Send payment link
from maintain_frontend.send_payment_link.routes import send_payment_link_bp
# View official search
from maintain_frontend.view_official_search.routes import view_official_search_bp
# Two Factor Authentication
from maintain_frontend.two_factor_authentication.routes import two_factor_authentication_bp


def register_blueprints(app):
    """Adds all blueprint objects into the app."""

    # General
    app.register_blueprint(general.general)

    # Common Map
    app.register_blueprint(map_bp)

    # Home
    app.register_blueprint(home_bp)

    # Search
    app.register_blueprint(search_bp)

    # Add Land Charge
    app.register_blueprint(add_land_charge_bp)

    # View Land Charge
    app.register_blueprint(view_llc_bp)

    # Modify Land Charge
    app.register_blueprint(modify_land_charge_bp)

    # Cancel Land Charge
    app.register_blueprint(cancel_land_charge_bp)

    # Create LLC1
    app.register_blueprint(create_llc1_bp)

    # Add LON
    app.register_blueprint(add_lon_bp)

    # Address finder
    app.register_blueprint(address_finder_bp)

    # View LON
    app.register_blueprint(view_lon_bp)

    # Modify LON
    app.register_blueprint(modify_lon_bp)

    # Cancel LON
    app.register_blueprint(cancel_lon_bp)

    # Reports
    app.register_blueprint(reports_bp)

    # Source Information
    app.register_blueprint(source_info_bp)

    # Send payment link
    app.register_blueprint(send_payment_link_bp)

    # View official search
    app.register_blueprint(view_official_search_bp)

    # Two Factor Authentication
    app.register_blueprint(two_factor_authentication_bp)

    app.logger.info("Blueprints registered")
