from enum import Enum, unique


@unique
class ReviewMap(Enum):
    """Map of JSON data name to display name for the review page."""
    applicant_name = 'Applicant name'
    applicant_address = 'Applicant address'
    charge_address = 'Location (dominant building)'
    charge_geographic_description = 'Location (dominant building) '
    geometry = 'Extent (dominant building)'
    servient_land_interest_description = 'Interest in land'
    form_a_file = 'Document: Form A and colour plan'
    temporary_lon_file = 'Document: Temporary certificate'
    tribunal_temporary_certificate_date = 'Temporary certificate date'
    tribunal_temporary_certificate_expiry_date = 'Temporary certificate expiry date'
    definitive_lon_file = 'Document: Definitive certificate'
    tribunal_definitive_certificate_date = 'Definitive certificate date'
    servient_height = 'Height of servient land development'
    servient_position = 'Covers all or part of extent'
