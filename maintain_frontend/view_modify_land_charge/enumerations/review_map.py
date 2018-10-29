from enum import Enum, unique


@unique
class ReviewMap(Enum):
    """Map of JSON data name to display name for the modify land charge page."""

    charge_description = 'Description'
    amount_originally_secured = 'Amount'
    rate_of_interest = 'Interest rate'
    land_compensation_paid = 'Advance payment'
    land_compensation_amount_type = 'Agreed or estimated'
    land_compensation_ownership = 'Interest in land'
    land_sold_description = 'Land sold'
    land_works_particulars = 'Work done'
    location_info = 'Location'
    geometry = 'Extent'
    charge_creation_date = 'Creation date'
    expiry_date = 'Expiry date'
    further_information = 'Source information or authority reference'
    amount_of_compensation = 'Total compensation'
