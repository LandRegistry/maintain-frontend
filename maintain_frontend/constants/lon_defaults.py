from maintain_frontend.constants.add_charge_reasons import AddChargeReason
from maintain_frontend.config import CONTACT_US_URL


class LonDefaults(object):
    """Defines the default values for a Light Obstruction Notice which the user cannot change."""
    charge_type = "Light obstruction notice"
    statutory_provision = "Rights of Light Act 1959 section 2(4)"
    instrument = AddChargeReason.certificate.value
    further_information_location = CONTACT_US_URL
