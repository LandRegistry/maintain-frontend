from enum import Enum, unique


@unique
class ReviewMap(Enum):
    """Map of JSON data name to display name for the review page."""

    originating_authority = 'Originating Authority'
    charge_type = 'Category'
    land_sold_description = 'Land sold'
    land_works_particulars = 'Work done'
    land_compensation_paid = 'Advance payment'
    land_compensation_amount_type = 'Agreed or estimated'
    land_capacity_description = 'Interest in land'
    amount_originally_secured = 'Amount'
    rate_of_interest = 'Interest rate'
    charge_creation_date = 'Creation date'
    geometry = 'Extent'
    charge_geographic_description = 'Location'
    charge_address = 'Location '
    expiry_date = 'Expiry date'
    further_information_location = 'Source information'
    further_information_reference = 'Authority reference'
    supplementary_information = 'Description'
    amount_of_compensation = 'Total compensation'
