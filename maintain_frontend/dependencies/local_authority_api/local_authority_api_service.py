from flask import current_app, g
from maintain_frontend.exceptions import ApplicationError
import json


class LocalAuthorityService(object):
    """Service class for making requests to /search/addresses endpoint."""
    def __init__(self, config):
        self.config = config
        self.url = "{}/v1.0/".format(config['LA_API_URL'])

    def get_bounding_box(self, authority):
        relative_path = "local-authorities/" + authority + "/bounding_box"
        request_path = self.url + relative_path
        current_app.logger.info("Calling local authority api via this URL: %s", request_path)
        return g.requests.get(request_path)

    def get_organisations(self):
        relative_path = "organisations"
        request_path = self.url + relative_path
        current_app.logger.info("Calling local authority api via this URL: %s", request_path)

        response = g.requests.get(request_path)

        if response.status_code == 200:
            current_app.logger.info("Organisations found")
            return response.json()
        else:
            current_app.logger.error("Error occurred when getting authorities")
            raise ApplicationError(500)

    def get_authorities_by_extent(self, bounding_box):
        request_path = self.url + 'local-authorities'
        current_app.logger.info("Calling local authority api by area via this URL: %s", request_path)
        response = g.requests.post(request_path,
                                   data=json.dumps(bounding_box),
                                   headers={'Content-Type': 'application/json'})

        if response.status_code == 200:
            current_app.logger.info("Authorities found")
            return response.json()
        elif response.status_code == 404:
            current_app.logger.info("No authorities found")
            return {}
        else:
            current_app.logger.error("Error occurred when getting authorities")
            raise ApplicationError(500)

    def is_extent_within_migrated_area(self, extent):
        request_path = self.url + 'local-authorities/is_extent_within_migrated_area'
        current_app.logger.info("Calling local authority api via this URL: {}".format(request_path))

        response = g.requests.post(request_path,
                                   data=extent,
                                   headers={'Content-Type': 'application/json'})

        if response.status_code == 200:
            current_app.logger.info("Succesfully determined if the given extent is within a migrated area")
            return response.json()
        else:
            current_app.logger.error("Failed to determine if the given extent is within a migrated area")
            raise ApplicationError(500)

    def get_source_information_for_organisation(self, organisation):
        request_path = self.url + "organisations/{}/source-information".format(organisation)
        current_app.logger.info("Calling local authority api via this URL: %s", request_path)

        response = g.requests.get(request_path)

        if response.status_code == 200:
            current_app.logger.info("Successfully retrieved source information for organisation")
            return response.json()
        else:
            current_app.logger.error("Failed to retrieve source information for organisation")
            raise ApplicationError(500)

    def add_source_information_for_organisation(self, source_information, organisation):
        request_path = self.url + "organisations/{}/source-information".format(organisation)
        current_app.logger.info("Calling local authority api via this URL: %s", request_path)

        response = g.requests.post(request_path,
                                   data=json.dumps({'source-information': source_information}),
                                   headers={'Content-Type': 'application/json'})

        if response.status_code == 201:
            current_app.logger.info("Successfully added source information for organisation")
            return response.json()
        else:
            current_app.logger.error("Failed to add source information for organisation")
            raise ApplicationError(500)

    def update_source_information_for_organisation(self, source_info_id, source_information, organisation):
        request_path = self.url + "organisations/{}/source-information/{}".format(organisation, source_info_id)
        current_app.logger.info("Calling local authority api via this URL: %s", request_path)

        response = g.requests.put(request_path,
                                  data=json.dumps({'source-information': source_information}),
                                  headers={'Content-Type': 'application/json'})

        if response.status_code == 200 or response.status_code == 201:
            current_app.logger.info("Successfully updated source information for organisation")
            return response.json()
        else:
            current_app.logger.error("Failed to update source information for organisation")
            raise ApplicationError(500)

    def delete_source_information_for_organisation(self, organisation, source_information_id):
        request_path = self.url + "organisations/{}/source-information/{}".format(organisation,
                                                                                  source_information_id)

        current_app.logger.info("Calling local authority api via this URL: %s", request_path)

        response = g.requests.delete(request_path)

        if not response.status_code == 204:
            current_app.logger.error("Failed to delete source information for organisation")
            raise ApplicationError(500)
