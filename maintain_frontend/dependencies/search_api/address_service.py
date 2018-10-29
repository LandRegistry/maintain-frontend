from flask import current_app, g


class AddressesService(object):
    """Service class for making requests to /search/addresses endpoint"""
    def __init__(self, config, address_api_version="v1"):
        self.config = config
        if address_api_version == "v1":
            self.url = "http://{}/search/addresses".format(config['SEARCH_API_URL'])
        else:
            self.url = "http://{}/{}/search/addresses".format(config['SEARCH_API_URL'], address_api_version)

    # Call the search api using postcode, uprn, or free text depending on input.
    def get_by(self, type, value):
        relative_path = "/" + type + "/" + value
        request_path = self.url + relative_path
        current_app.logger.info("Calling search api via this URL: %s", request_path)
        return g.requests.get(request_path)
