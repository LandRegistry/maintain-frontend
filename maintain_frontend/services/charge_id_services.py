from flask import current_app
from maintain_frontend.exceptions import ApplicationError
import re

CHARGE_NUMBER_REGEX = '^(llc|LLC)(-)?([0123456789BCDFGHJKLMNPQRSTVWXYZ]){1,6}$'


def calc_display_id(local_land_charge_id):
    characters = '0123456789BCDFGHJKLMNPQRSTVWXYZ'
    encoded = ''
    while local_land_charge_id > 0:
        local_land_charge_id, remainder = divmod(local_land_charge_id, 31)
        encoded = characters[remainder] + encoded
    return "LLC-{}".format(encoded)


def validate_charge_id(charge_id):
    if not re.match(CHARGE_NUMBER_REGEX, charge_id):
        current_app.logger.warn("Invalid charge id '{}' requested - Returning error".format(charge_id))
        raise ApplicationError(404)
