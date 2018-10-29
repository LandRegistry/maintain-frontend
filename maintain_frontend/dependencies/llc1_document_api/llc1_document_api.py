from flask import current_app, g
from maintain_frontend.exceptions import ApplicationError


class LLC1DocumentService(object):
    """Service class for making requests to /search/addresses endpoint."""
    def __init__(self, config):
        self.config = config
        self.url = current_app.config['LLC1_API_URL']

    # Call the LLC1 Document api using given description and extents.
    def generate(self, description, extents):

        payload = {
            'description': description,
            'extents': extents,
            'source': 'MAINTAIN'
        }

        current_app.logger.info("Submit LLC1 search request")
        response = g.requests.post(self.url,
                                   json=payload,
                                   headers={'Content-Type': 'application/json'})

        if response.status_code != 201:
            current_app.logger.warning('Failed to create LLC1')
            raise ApplicationError('Failed to create LLC1')

        return response.json()
