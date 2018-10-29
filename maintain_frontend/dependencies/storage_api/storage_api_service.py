from flask import current_app, g
from urllib.parse import parse_qsl, urlparse
from maintain_frontend.exceptions import ApplicationError


class StorageAPIService(object):

    """Service class for making requests to /search/addresses endpoint."""
    def __init__(self, config):
        self.config = config
        self.url = config['STORAGE_API_URL']

    def save_files(self, files, bucket, subdirectories=None, scan=False):
        params = {}
        if subdirectories:
            params["subdirectories"] = subdirectories
        if scan:
            params["scan"] = scan

        request_path = self.url + "/" + bucket

        current_app.logger.info("Calling storage api via this URL: %s", request_path)
        return g.requests.post(request_path, files=files, params=params)

    def get_external_url(self, file_id, bucket, subdirectories=None):
        current_app.logger.info("Generate external URL for {}".format(file_id))
        params = {}
        if subdirectories:
            params["subdirectories"] = subdirectories

        request_path = "{}/{}/{}/external-url".format(self.url, bucket, file_id)

        current_app.logger.info("Calling storage api via this URL: {}".format(request_path))
        response = g.requests.get(request_path, params=params)

        current_app.logger.info("Calling storage api responded with status: {}".format(response.status_code))

        if response.status_code == 200:
            json = response.json()
            return json['external_reference']
        if response.status_code == 404:
            return None

        current_app.logger.warning(
            'Failed to get external url - TraceID : {} - Status: {}, Message: {}'.format(
                g.trace_id,
                response.status_code,
                response.text))
        raise ApplicationError(500)

    def get_external_url_from_path(self, path):
        current_app.logger.info("Generate external URL for path {}".format(path))
        params = None
        if urlparse(path).query:
            params = dict(parse_qsl(urlparse(path).query))
            request_path = "{}/{}/external-url".format(self.url, path[:path.find('?')])
        else:
            request_path = "{}/{}/external-url".format(self.url, path)

        current_app.logger.info("Calling storage api via this URL: {}".format(request_path))
        response = g.requests.get(request_path, params=params)

        if response.status_code == 200:
            json = response.json()
            return json['external_reference']
        if response.status_code == 404:
            return None

        current_app.logger.warning(
            'Failed to get external url - TraceID : {} - Status: {}, Message: {}'.format(
                g.trace_id,
                response.status_code,
                response.text))
        raise ApplicationError(500)

    @staticmethod
    def get_external_url_for_document_url(document_url):
        current_app.logger.info("Generate external URL for document_url {}".format(document_url))
        request_path = "{}/external-url".format(document_url)

        current_app.logger.info("Calling storage api via this URL: {}".format(request_path))
        response = g.requests.get(request_path)

        current_app.logger.info("Calling storage api responded with status: {}".format(response.status_code))

        if response.status_code == 200:
            json = response.json()
            return json['external_reference']
        if response.status_code == 404:
            current_app.logger.warning("Failed to find external document url for url {}".format(document_url))
            raise ApplicationError(404)

        current_app.logger.warning(
            'Failed to get external url - TraceID : {} - Status: {}, Message: {}'.format(
                g.trace_id,
                response.status_code,
                response.text))
        raise ApplicationError(500)
