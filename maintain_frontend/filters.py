import json
from maintain_frontend.services.charge_id_services import calc_display_id


def register_filters(app):
    # Convert string to json object for dict-access
    @app.template_filter('to_json_obj')
    def to_json_obj(json_str):
        return json.loads(json_str)

    @app.template_filter('calc_display_id')
    def calc_display_id_filter(local_land_charge):
        return calc_display_id(local_land_charge)
