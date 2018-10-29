from enum import Enum, unique


@unique
class AddChargeReason(Enum):
    """Defines the reason a charge can be raised for.


    In HTML pages the key should be used as the id and value posted in forms, and the value as the displayed text.
    """
    acceptance = 'Acceptance'
    certificate = 'Certificate'
    covenants = 'Covenants'
    deed = 'Deed'
    deed_of_modification = 'Deed of modification'
    notice = 'Notice'
    order = 'Order'
    resolution = 'Resolution'
    scheme = 'Scheme'
    transfer = 'Transfer'
    undertaking = 'Undertaking'
