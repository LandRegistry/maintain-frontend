/*global map ol normal MAP_HELPERS*/
var VIEW_PAGE = {}

$(function() {
    // Remove map controls (draw tools) and interactions (zooming, panning, etc.)
    map.getControls().clear();
    map.getInteractions().clear();
    map.addControl(new ol.control.Attribution({collapsed: false,
                                               collapsible: false,
                                               className: 'ol-attribution ol-attribution-small'}));

    var attribution = new ol.Attribution({
                          html: '© Crown copyright'
                      })
    map.getLayers().item(0).getSource().setAttributions(attribution);

    // Add New Layer to Open Layers for LLC
    map.addLayer(VIEW_PAGE.llc_layer);

    if (charge_extent != '') {
        map.getView().fit(VIEW_PAGE.llc_source.getExtent(), {maxZoom: '15'});
    }

    MAP_HELPERS.remove_openlayers_attribution_link();
});

// Open Layers Local Land Charge Display Layer
charge_extent = $('#charge_extent').val();
options = {dataProjection: 'EPSG:27700', featureProjection: 'EPSG:27700'};
VIEW_PAGE.llc_features = new ol.format.GeoJSON().readFeatures(charge_extent, options);
VIEW_PAGE.llc_source = new ol.source.Vector({ features: VIEW_PAGE.llc_features });
VIEW_PAGE.llc_layer = new ol.layer.Vector({ source: VIEW_PAGE.llc_source, style: normal });
