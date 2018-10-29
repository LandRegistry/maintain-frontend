var wfs_server_url = "wfs_server_url"
var mastermap_api_key = "mastermap_api_key"

describe("Snap to vector layer javascript tests", function () {
    beforeEach(function () {
        var setupVars = '<script>  var wfs_server_url = "wfs_server_url"; var mastermap_api_key = "mastermap_api_key"</script>'
        document.body.insertAdjacentHTML('beforebegin', setupVars)

    });

    it("enabling the layer adds the snap to vector layer to map", function () {
        spyOn(map, 'addLayer')

        SNAP_TO_VECTOR_LAYER.enable()

        expect(map.addLayer).toHaveBeenCalledTimes(1)
        expect(SNAP_TO_VECTOR_LAYER.vectorsOnMap).toEqual(true)

    });

    it("disabling the layer removes the snap to vector layer from the map", function () {
        spyOn(map, 'removeLayer')

        SNAP_TO_VECTOR_LAYER.disable()

        expect(map.removeLayer).toHaveBeenCalledTimes(1)
        expect(SNAP_TO_VECTOR_LAYER.vectorsOnMap).toEqual(false)

    });

    it("Layer has correct url format and return format", function () {

        expect(SNAP_TO_VECTOR_LAYER.layer.getSource().getFormat()).toEqual(new ol.format.GeoJSON())

        var url_function = SNAP_TO_VECTOR_LAYER.layer.getSource().getUrl();
        var extent = new ol.extent.boundingExtent([[137738.0354,383.7986],[633717.1256,669903.6353]]);
        expect(url_function(extent)).toEqual('wfs_server_url/mastermap_api_key/wfs?service=WFS&version=1.1.0&request=GetFeature&typename=OS.MMTopo:SnapLines&maxFeatures=2000&outputFormat=application/json&srsname=EPSG:27700&bbox=137738.0354,383.7986,633717.1256,669903.6353')

    });
});
