from unittest import TestCase
from maintain_frontend.llc1.validation.search_extent_validator import SearchExtentValidator


NO_GEOMETRY = None
FEATURE_COLLECTION = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[1, 2], [3, 4], [5, 6], [1, 2]]]
            }
        }
    ]
}


class TestSearchExtentValidator(TestCase):
    def test_no_geometry_fails(self):
        result = SearchExtentValidator.validate(NO_GEOMETRY).errors
        self.assertEqual(len(result), 1)
        self.assertEqual(result['map'].inline_message, 'Extent is required')
        self.assertEqual(result['map'].summary_message, 'Draw the extent')

    def test_feature_collection_passes(self):
        result = SearchExtentValidator.validate(FEATURE_COLLECTION).errors
        self.assertEqual(len(result), 0)
