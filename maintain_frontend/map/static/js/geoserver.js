/*global GEOSERVER_CONFIG ol MAP_CONFIG*/
/*exported configure_geoserver_layer_for_user*/

var GEOSERVER_CONFIG = {}

GEOSERVER_CONFIG.boundaries_layer;

function configure_geoserver_layer_for_user(is_lr, organisation, geoserver_url, geoserver_token) {
    // handle the authority which have apostrophes in them
    var organisation_escaped = organisation.replace("&#39;","\'");

    GEOSERVER_CONFIG.boundaries_layer = get_boundary_layer(geoserver_url, geoserver_token, 'authority_boundary_maintain',
      organisation_escaped, MAP_CONFIG.boundary_layer_zindex);

}

function get_boundary_layer(geoserver_url, geoserver_token, style, user_authority, layer_zindex) {
    var params = {
        'LAYERS': 'llc:boundaries_organisation_combined',
        'VERSION': '1.1.1',
        'FORMAT': 'image/png',
        'TILED': true,
        'STYLES': style
    };

    if (user_authority) {
        params['ENV'] = 'la_name:' + user_authority;
    }

    var layer = new ol.layer.Tile({
        source: new ol.source.TileWMS({
            url: geoserver_url + '/geoserver/llc/' + geoserver_token + '/wms?',
            params: params
        }),
        zIndex: layer_zindex
    });

    return layer;
}