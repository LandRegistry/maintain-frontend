$(function() {
    // Map Draw Feature Added
    MAP_CONFIG.draw_features.on('add', function (event) {
        geometry = event.element.getGeometry();
        search.chargesInArea(geometry);
        MAP_CONTROLS.enableButton('.map-button-polygon', false);
        MAP_CONTROLS.removeActiveControl();
        MAP_CONTROLS.vectorControls.disableOverride = true;
        MAP_CONTROLS.vectorControls.disableControls()
    });

    $("#map-button-edit").on('edit:toggled', function() {
        MAP_CONTROLS.current_interaction.on('modifyend', function(event) {
            geometry = event.features.getArray()[0].getGeometry()
            search.chargesInArea(geometry)
        });
    });

    MAP_CONFIG.draw_features.on('remove', function (event) {
        search.llcSource.clear()
        search.searchViewModel.charges.removeAll();
        search.searchViewModel.categories().forEach(function(category) {
            category.clearCharges();
        });
        $("#map-button-polygon").removeAttr("disabled");
        MAP_CONTROLS.vectorControls.disableOverride = false
        if (MAP_HELPERS.get_zoom_level(map) >= MAP_CONFIG.vectorControlsZoomThreshold) {
                MAP_CONFIG.vectorControls.enableControls()
        }
    });

    map.on("dblclick", function (e) {
        if (MAP_CONTROLS.current_interaction instanceof ol.interaction.Draw) {
            MAP_CONTROLS.current_interaction = null;
            return false;
        }
    });

    var isChargeLayer = function(layer) {
        return layer === search.llcLayer && MAP_CONTROLS.current_style === draw_layer_styles.NONE;
    };

    var getFeatureToHighlight = function (pixel) {
        var topLevelFeature = undefined;
        map.forEachFeatureAtPixel(pixel, function(feature, layer) {
            if (isChargeLayer(layer) && !topLevelFeature) {
                var category = feature.getProperties().charge.category;
                if(category.checked()) {
                    topLevelFeature = feature;
                }
            }
        });
        return topLevelFeature;
    };

    map.on('pointermove', function(browserEvent) {
        var currentHighlightedFeature = search.searchViewModel.highlightedFeature();
        if(currentHighlightedFeature && currentHighlightedFeature.getStyle() !== llc_layer_styles.hidden) {
            featureHelpers.setStyleForFeature(currentHighlightedFeature, llc_layer_styles.standard_style);
        }

        var topLevelFeature = getFeatureToHighlight(browserEvent.pixel);
        if(topLevelFeature && topLevelFeature.getStyle() !== llc_layer_styles.hidden) {
            featureHelpers.setStyleForFeature(topLevelFeature, llc_layer_styles.selected_style);
        }

        search.searchViewModel.highlightedFeature(topLevelFeature);
        MAP_HELPERS.remove_interaction_if_polygon_button_disabled(map);
    });
});