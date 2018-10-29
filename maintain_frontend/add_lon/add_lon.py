from flask import redirect, url_for, g, current_app
from maintain_frontend.models import LightObstructionNoticeItem, PaymentInfo
from maintain_frontend.constants.lon_defaults import LonDefaults
from maintain_frontend.config import SCHEMA_VERSION


def register_routes(bp):
    bp.add_url_rule('/add-light-obstruction-notice',
                    view_func=new, methods=['GET'])


def new():
    """This will setup state for adding a new land charge and redirect to the starting page."""
    g.session.add_lon_charge_state = LightObstructionNoticeItem()

    # Apply Default Values
    g.session.add_lon_charge_state.charge_type = LonDefaults.charge_type
    if g.session.add_charge_state is not None and g.session.add_charge_state.statutory_provision is not None:
        g.session.add_lon_charge_state.statutory_provision = g.session.add_charge_state.statutory_provision
    else:
        g.session.add_lon_charge_state.statutory_provision = LonDefaults.statutory_provision

    if g.session.add_charge_state is not None and g.session.add_charge_state.instrument is not None:
        g.session.add_lon_charge_state.instrument = g.session.add_charge_state.instrument
    else:
        g.session.add_lon_charge_state.instrument = LonDefaults.instrument

    g.session.add_lon_charge_state.further_information_location = LonDefaults.further_information_location
    g.session.add_lon_charge_state.schema_version = SCHEMA_VERSION

    g.session.payment_info = PaymentInfo()
    g.session.filenames = None
    g.session.redirect_route = None
    g.session.edited_fields = {}

    g.session.commit()
    current_app.logger.info("Created new session object: %s",
                            g.session.add_lon_charge_state.to_json())

    current_app.logger.info("Redirecting to: %s",
                            url_for("add_lon.get_applicant_info"))
    return redirect(url_for("add_lon.get_applicant_info"))
