/*global ol map mastermap_api_key*/

var MASTER_MAP_VECTOR_LAYER = {}

var vectorSource = new ol.source.Vector({
    format: new ol.format.GeoJSON(),
    url: function(extent) {
        return wfs_server_url + '/' + mastermap_api_key + '/wfs?service=WFS&' +
               'version=1.1.0&request=GetFeature&typename=OS.MMTopo:BuildingPolys&' +
               'maxFeatures=2000&outputFormat=application/json&srsname=EPSG:27700&' +
               'bbox=' + extent.join(',')
    },
    strategy: ol.loadingstrategy.bbox
});

MASTER_MAP_VECTOR_LAYER.layer = new ol.layer.Vector({
    source: vectorSource,
    style: new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: 'rgba(0, 0, 255, 0)',
            width: 1
        })
    })
})

MASTER_MAP_VECTOR_LAYER.vectorsOnMap = false

MASTER_MAP_VECTOR_LAYER.enable = function() {
    if (!MASTER_MAP_VECTOR_LAYER.vectorsOnMap) {
        map.addLayer(MASTER_MAP_VECTOR_LAYER.layer)
        MASTER_MAP_VECTOR_LAYER.vectorsOnMap = true
    }
    MASTER_MAP_VECTOR_LAYER.layer.getSource().clear()
}

MASTER_MAP_VECTOR_LAYER.disable = function() {
    if (MASTER_MAP_VECTOR_LAYER.vectorsOnMap) {
        map.removeLayer(MASTER_MAP_VECTOR_LAYER.layer)
        MASTER_MAP_VECTOR_LAYER.vectorsOnMap = false
    }
}
