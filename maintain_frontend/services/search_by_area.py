import json

from maintain_frontend.dependencies.search_api.local_land_charge_service import LocalLandChargeService


class SearchByArea(object):
    def __init__(self, logger, config):
        self.logger = logger
        self.local_land_charge_service = LocalLandChargeService(config)

    def process(self, bounding_box):
        response = dict()
        search_response = self.process_request(bounding_box)

        response['status'] = search_response.status_code
        if search_response.status_code == 200:
            response['data'] = search_response.json()
        return response

    def process_request(self, bounding_box):
        if bounding_box:
            return self.get_results_for_boundary(bounding_box)

    def get_results_for_boundary(self, bounding_box):
        self.logger.info("Searching area by bounding box")
        return self.local_land_charge_service.get(self.prepare_bounding_box(bounding_box))

    @staticmethod
    def prepare_bounding_box(bounding_box):
        return SearchByArea.build_bounding_box_json(bounding_box)

    @staticmethod
    def build_bounding_box_json(bounding_box):
        geo_dict = {
            "type": "Polygon",
            "coordinates": json.loads(bounding_box),
            "crs": {
                "type": "name",
                "properties": {
                    "name": "EPSG:27700"
                }
            }
        }

        return json.dumps(geo_dict)
