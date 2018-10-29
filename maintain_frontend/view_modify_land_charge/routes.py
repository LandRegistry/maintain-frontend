from flask import Blueprint
import maintain_frontend.view_modify_land_charge.view_land_charge
import maintain_frontend.view_modify_land_charge.view_land_charge_history
import maintain_frontend.view_modify_land_charge.cancel_land_charge
import maintain_frontend.view_modify_land_charge.modify_land_charge
import maintain_frontend.view_modify_land_charge.edit_location
import maintain_frontend.view_modify_land_charge.edit_address_for_charge
import maintain_frontend.view_modify_land_charge.edit_expiry
import maintain_frontend.view_modify_land_charge.edit_additional_info
import maintain_frontend.view_modify_land_charge.edit_charge_date
import maintain_frontend.view_modify_land_charge.edit_charge_description
import maintain_frontend.view_modify_land_charge.edit_financial_charge
import maintain_frontend.view_modify_land_charge.edit_land_compensation_ownership
import maintain_frontend.view_modify_land_charge.edit_land_compensation_payment
import maintain_frontend.view_modify_land_charge.edit_land_compensation_land_sold
import maintain_frontend.view_modify_land_charge.edit_location_confirmation
import maintain_frontend.view_modify_land_charge.update_location_confirmation
import maintain_frontend.view_modify_land_charge.cancel_location_confirmation

view_llc_bp = Blueprint('view_land_charge', __name__, static_folder='static',
                        static_url_path='/static/view_modify_land_charge',
                        template_folder='templates', url_prefix='/view-local-land-charge')

cancel_land_charge_bp = Blueprint('cancel_land_charge', __name__, static_folder='static',
                                  static_url_path='/static/view_modify_land_charge',
                                  template_folder='templates', url_prefix='/cancel-local-land-charge')

modify_land_charge_bp = Blueprint('modify_land_charge', __name__, static_folder='static',
                                  static_url_path='/static/view_modify_land_charge',
                                  template_folder='templates', url_prefix='/update-local-land-charge')

# View
maintain_frontend.view_modify_land_charge.view_land_charge.register_routes(view_llc_bp)
maintain_frontend.view_modify_land_charge.view_land_charge_history.register_routes(view_llc_bp)

# Cancel
maintain_frontend.view_modify_land_charge.cancel_land_charge.register_routes(cancel_land_charge_bp)
maintain_frontend.view_modify_land_charge.cancel_location_confirmation.register_routes(cancel_land_charge_bp)

# Modify
maintain_frontend.view_modify_land_charge.modify_land_charge.register_routes(modify_land_charge_bp)
maintain_frontend.view_modify_land_charge.edit_location.register_routes(modify_land_charge_bp)
maintain_frontend.view_modify_land_charge.edit_location_confirmation.register_routes(modify_land_charge_bp)
maintain_frontend.view_modify_land_charge.edit_address_for_charge.register_routes(modify_land_charge_bp)
maintain_frontend.view_modify_land_charge.edit_expiry.register_routes(modify_land_charge_bp)
maintain_frontend.view_modify_land_charge.edit_additional_info.register_routes(modify_land_charge_bp)
maintain_frontend.view_modify_land_charge.edit_charge_date.register_routes(modify_land_charge_bp)
maintain_frontend.view_modify_land_charge.edit_charge_description.register_routes(modify_land_charge_bp)
maintain_frontend.view_modify_land_charge.edit_financial_charge.register_routes(modify_land_charge_bp)
maintain_frontend.view_modify_land_charge.edit_land_compensation_ownership.register_routes(modify_land_charge_bp)
maintain_frontend.view_modify_land_charge.edit_land_compensation_payment.register_routes(modify_land_charge_bp)
maintain_frontend.view_modify_land_charge.edit_land_compensation_land_sold.register_routes(modify_land_charge_bp)
maintain_frontend.view_modify_land_charge.update_location_confirmation.register_routes(modify_land_charge_bp)
