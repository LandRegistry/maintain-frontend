def build_extents_from_features(features):
    extents = []
    for feature in features['features']:
        geo_dict = {
            "type": feature['geometry']['type'],
            "coordinates": feature['geometry']['coordinates'],
            "crs": {
                "type": "name",
                "properties": {
                    "name": "EPSG:27700"
                }
            }
        }
        extents.append(geo_dict)

    collection = {
        "type": "geometrycollection",
        "geometries": extents
    }
    return collection
