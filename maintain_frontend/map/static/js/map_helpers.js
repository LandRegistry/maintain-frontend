/*global ol MAP_CONFIG map $ GEOSERVER_CONFIG*/

var MAP_HELPERS = {};

// This function will return the current zoom level.
// If the zoom level is undefined it will return the max zoom level.
// The map.getView().getZoom() function returns undefined when loading the search page with a search term saved in session (eg. when refreshing the page after searching).
// This function resolves the issue where no extents are drawn on the map when the page is initially loaded and zooms into the extent area.
// This is due to a rounding error when the zoom level is calculated to be outside of the resolution constraints
(function(MAP_HELPERS) {
    MAP_HELPERS.get_zoom_level = function(map) {
        var current_zoom_level = map.getView().getZoom()
        if (current_zoom_level || current_zoom_level === 0) {
            return Math.round(current_zoom_level)
        } else {
            return MAP_CONFIG.max_zoom_level;
        }
    };

    MAP_HELPERS.zoom_to_boundary = function(is_lr, organisation) {
        // handle the authority which have apostrophes in them
        var organisation_escaped = organisation.replace("&#39;","\'")

        if (is_lr) {
            var extent = new ol.extent.boundingExtent([[137738.0354,383.7986],[633717.1256,669903.6353]]);
            map.getView().fit(extent, {constrainResolution: false, duration: 500, easing: ol.easing.linear});
        } else {
            $.getJSON($SCRIPT_ROOT + '/_authorities/' + encodeURIComponent(organisation_escaped) + '/boundingbox')
                .done(function(json){
                    var geojson = new ol.format.GeoJSON();
                    var feature = geojson.readFeature(json);
                    extent = feature.getGeometry().getExtent();
                    map.getView().fit(extent, {constrainResolution: false, duration: 500, easing: ol.easing.linear});
                })
                .fail(function(json) {
                    extent = new ol.extent.boundingExtent([[137738.0354,383.7986],[633717.1256,669903.6353]]);
                    map.getView().fit(extent, {constrainResolution: false, duration: 500, easing: ol.easing.linear});
                });
        }
    };

    // Ensures that tabbing order for controls is correct by defining the order in which controls are added to the map
    MAP_HELPERS.init_controls = function(map, controls) {
        map.addControl(controls);
        map.addControl(new ol.control.Zoom());
        map.addControl(new ol.control.ScaleLine());
        map.addControl(new ol.control.Attribution({collapsed: false, collapsible: false}));

        MAP_HELPERS.remove_openlayers_attribution_link();
    };

    MAP_HELPERS.remove_openlayers_attribution_link = function() {
        // Remove Openlayers icon/link from the attribution
        var attributions = document.getElementsByClassName('ol-attribution ol-unselectable ol-control ol-uncollapsible');
        if (attributions.length > 0) {
            var ul = attributions[0].childNodes[0];
            ul.removeChild(ul.childNodes[0]);
        }
    }

    // Fixes issue where user can triple-click after drawing a polygon to potentially draw more shapes than intended.
    // Checks if draw interaction is still active and the polygon button is disabled.
    // If true, the draw interaction is removed.
    MAP_HELPERS.remove_interaction_if_polygon_button_disabled = function(map) {
        var polygonButtonDisabled = $('#map-button-polygon').prop('disabled');

        if (polygonButtonDisabled) {
            map.getInteractions().forEach(function (interaction) {
                if(interaction instanceof ol.interaction.Draw) {
                    map.removeInteraction(interaction);
                }
            });
        }
    }
})(MAP_HELPERS);
