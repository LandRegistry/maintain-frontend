/*global proj4 ol MAP_CONTROLS draw_layer_styles mastermap_api_key document MAP_UNDO*/
// Define British National Grid Projection - we'll use this to convert points to/from OpenLayers ESPG:3857 Format
proj4.defs('EPSG:27700', '+proj=tmerc +lat_0=49 +lon_0=-2 +k=0.9996012717 ' +
    '+x_0=400000 +y_0=-100000 +ellps=airy ' +
    '+towgs84=446.448,-125.157,542.06,0.15,0.247,0.842,-20.489 ' +
    '+units=m +no_defs');

var MAP_CONFIG = {};

(function(MAP_CONFIG) {
    // Map Default Position
    MAP_CONFIG.default_center = [385727.58, 335143.72];
    MAP_CONFIG.default_zoom = 0;
    MAP_CONFIG.vectorControlsZoomThreshold = 13;
    MAP_CONFIG.max_zoom_level = 15;
    MAP_CONFIG.draw_control_id = 'draw-controls';

    MAP_CONFIG.base_layer_zindex = 0;
    MAP_CONFIG.boundary_layer_zindex = 1;
    MAP_CONFIG.non_migrated_layer_zindex = 2;
    MAP_CONFIG.llc_layer_zindex = 3;
    MAP_CONFIG.draw_layer_zindex = 4;
    MAP_CONFIG.highlighted_charge_layer_zindex = 5;

    // Draw Source
    MAP_CONFIG.draw_features = new ol.Collection();
    MAP_CONFIG.draw_source = new ol.source.Vector({ features: MAP_CONFIG.draw_features });
    MAP_CONFIG.draw_layer = new ol.layer.Vector({
        source: MAP_CONFIG.draw_source,
        style: draw_layer_styles.style[draw_layer_styles.NONE],
        zIndex: MAP_CONFIG.draw_layer_zindex
    });
    MAP_CONFIG.projection = ol.proj.get('EPSG:27700');
    // Fixed resolutions to display the map at (pixels per ground unit (meters when
    // the projection is British National Grid))
    MAP_CONFIG.resolutions = [
        //res level scale
        2800.0000, // 0 10000000.0
        1400.0000, // 1 5000000.0
        700.0000, // 2 2500000.0
        280.0000, // 3 1000000.0
        140.0000, // 4 500000.0
        70.0000, // 5 250000.0
        28.0000, // 6 100000.0
        21.0000, // 7 75000.0
        14.0000, // 8 50000.0
        7.0000, // 9 25000.0
        2.8000, // 10 10000.0
        1.4000, // 11 5000.0
        0.7000, // 12 2500.0
        0.3500, // 13 1250.0
        0.1750, // 14 625.0
        0.0875 // 15 312.5
    ];

    // Master Map Vector Layer
    MAP_CONFIG.snap_to = new MAP_CONTROLS.snap_to();
    MAP_CONFIG.vectorControls = MAP_CONTROLS.vectorControls;

    var getTermsAndConditions = function(osTermsLink) {
        var termsLine1 = 'Use of address and mapping data (including the link between the address ';
        var termsLine2 = 'and its location) is subject to <a href="' + osTermsLink + '" target="_blank">Ordnance Survey licence terms and conditions</a>';
        return termsLine1 + '<br>' + termsLine2;
    };

    MAP_CONFIG.setBaseLayer = function(zIndex, res, proj, osTermsLink) {
        // Extent of the map in units of the projection (these match our base map)
        var extent = [0, 0, 700000, 1300000];

        proj = ol.proj.get('EPSG:27700');
        proj.setExtent(extent);

        MAP_CONFIG.base_layer = new ol.layer.Tile({
            extent: extent,
            opacity: 1.0,
            source: new ol.source.TileImage({
                attributions: new ol.Attribution({
                    html: getTermsAndConditions(osTermsLink)
                }),
                crossOrigin: null,
                projection: proj,
                tileGrid: new ol.tilegrid.TileGrid({
                    origin: [extent[0], extent[1]],
                    resolutions: res
                }),
                tileUrlFunction: function(tileCoord, pixelRatio, projection) {
                    if (!tileCoord) {
                        return "";
                    }

                    var x = tileCoord[1];
                    var y = tileCoord[2];
                    var z = tileCoord[0];

                    if (x < 0 || y < 0) {
                        return "";
                    }

                    var url = wmts_server_url + '/' + mastermap_api_key + '/' + map_base_layer_view_name + '/' + z +'/'+ x +'/'+ y +'.png';
                    return url;
                }
            }),
            zIndex: zIndex
        });
    };
})(MAP_CONFIG);

MAP_CONFIG.draw_features.on('change:length', function(event) {
    var count = MAP_CONFIG.draw_features.getLength();
    MAP_CONTROLS.enableControls(count !== 0);
    // Force the current state to update on completion of drawing a feature
    // because 'drawend' is called before the geometry is added to the map.
    // Is also called on remove, but that should be side-effect free.
    MAP_UNDO.update_current_state();
});
