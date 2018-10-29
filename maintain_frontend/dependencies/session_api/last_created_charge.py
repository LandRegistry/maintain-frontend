class LastCreatedCharge(object):
    """Model to hold last created charge."""

    def __init__(self):
        """Initialize instance of the LastCreatedCharge."""
        self.charge_id = None
        self.registration_date = None
        self.entry_number = None

    @staticmethod
    def from_dict(state_json):
        """Build AddChargeState object from json dictionary.


        :param state_json: Json Dictionary representing the add charge state.
        :return: AddChargeState object.
        """
        state = LastCreatedCharge()
        if 'charge_id' in state_json:
            state.charge_id = state_json['charge_id']
        if 'registration_date' in state_json:
            state.registration_date = state_json['registration_date']
        if 'entry_number' in state_json:
            state.entry_number = state_json['entry_number']
        return state
