from flask import render_template
from maintain_frontend.decorators import requires_permission
from maintain_frontend.constants.permissions import Permissions


def register_routes(bp):
    bp.add_url_rule('/add-local-land-charge/charge-type/not-known-contact-HMLR',
                    view_func=get_subcategory_not_known, methods=['GET'])


@requires_permission([Permissions.add_llc])
def get_subcategory_not_known():
    return render_template('charge_subcategories/subcategory_not_known.html')
