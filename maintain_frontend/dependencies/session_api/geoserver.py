class Geoserver(object):
    """Model to hold geoserver details."""

    def __init__(self):
        """Initialize Geoserver object."""
        self.token = None
        self.token_expiry = None

    def to_dict(self):
        """Returns dictionary representation of object.


        :return: dictionary holding geoserver information.
        """
        return {
            "token": self.token,
            "token_expiry": self.token_expiry
        }

    @staticmethod
    def from_dict(user_json):
        """Builds Geoserver object from json dictionary.


        :param user_json: Json dictionary holding geoserver information.
        :return: geoserver object.
        """
        geoserver = Geoserver()
        geoserver.token = user_json['token']
        geoserver.token_expiry = user_json['token_expiry']
        return geoserver
