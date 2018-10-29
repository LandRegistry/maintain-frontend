from flask import current_app
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.models import LocalLandChargeHistoryItem, LightObstructionNoticeItem
from maintain_frontend.services.charge_id_services import validate_charge_id


def get_history_update_info_by_charge_id(charge_id, local_land_charge_service):
    hist_response = local_land_charge_service.get_history_for_charge(charge_id)

    if hist_response.status_code == 404:
        current_app.logger.info("Search service reports '{}' not found - Returning error".format(charge_id))
        raise ApplicationError(404)

    hist_response.raise_for_status()
    history_items = list(reversed(LocalLandChargeHistoryItem.from_json(hist_response.json())))

    if len(history_items) > 1:
        updated_date = history_items[0].entry_timestamp.strftime('%-d %B %Y')
        updated = True
    else:
        updated_date = None
        updated = False

    return updated, updated_date


def get_lon_by_charge_id(charge_id, local_land_charge_service):
    validate_charge_id(charge_id)

    current_app.logger.info("Retrieving charge information from charge_id='{}'".format(charge_id))

    response = local_land_charge_service.get_by_charge_number(charge_id)

    if response.status_code == 404:
        current_app.logger.info("Search service reports '{}' not found - Returning error".format(charge_id))
        raise ApplicationError(404)

    response.raise_for_status()

    charge_item = LightObstructionNoticeItem.from_json(response.json()[0]['item'])
    display_id = response.json()[0]['display_id']
    current_app.logger.info("Retrieved charge for local_land_charge='{}'".format(charge_id))

    return display_id, charge_item
