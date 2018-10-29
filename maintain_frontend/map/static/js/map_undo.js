/*global MAP_CONTROLS MAP_CONFIG document ol draw_layer_styles*/

var MAP_UNDO = {};

MAP_UNDO.current_state = null;
MAP_UNDO.undo_stack = [];
MAP_UNDO.undoing = false;

MAP_UNDO.store_state = function() {
    // The trap on !undoing is used here and below to stop the undo process
    // storing states it creates as undoable-to states...
    if(!MAP_UNDO.undoing) {
        if(MAP_UNDO.current_state != null) {
            MAP_UNDO.undo_stack.push(MAP_UNDO.current_state);
            // Limit growth of undo stack [AC3]
            if(MAP_UNDO.undo_stack.length > 10) {
                MAP_UNDO.undo_stack = MAP_UNDO.undo_stack.slice(MAP_UNDO.undo_stack.length - 10)
            }
        }

        MAP_UNDO.current_state = MAP_UNDO.get_geometries();
        MAP_UNDO.enable_undo_button(true);
    }
};

MAP_UNDO.update_current_state = function() {
    MAP_UNDO.current_state = MAP_UNDO.get_geometries();
};

MAP_UNDO.clear_undo_stack = function() {
    MAP_UNDO.undo_stack = [];
    MAP_UNDO.enable_undo_button(false);
};

MAP_UNDO.undo = function() {
    if(MAP_CONTROLS.current_interaction && MAP_CONTROLS.current_interaction instanceof ol.interaction.Draw) {
        // There is a bug here... if we've removed some stuff then swtched to drawing,
        // then 'removeLastPoint' will fail because it's invalid to call it and we'd want to
        // call the main block of code...
        MAP_UNDO.openlayers_undo();
    } else {
        MAP_UNDO.remove_undo();
    }
};

MAP_UNDO.openlayers_undo = function() {
    try {
        MAP_CONTROLS.current_interaction.removeLastPoint();
    } catch(error) {
        // When you remove a feature, then select a draw button before undoing,
        // there's no way to tell that the last action was actually a remove. In
        // this case, catch the error generated...
        if (error instanceof TypeError) {
            MAP_UNDO.remove_undo();
        }
    }
};

MAP_UNDO.remove_undo = function() {
    // The trap on !undoing is used here and above to stop the undo process
    // storing states it creates as undoable-to states...
    if(!MAP_UNDO.undoing) {
        MAP_UNDO.undoing = true;

        if(MAP_UNDO.undo_stack.length > 0) {
            MAP_UNDO.current_state = MAP_UNDO.undo_stack.pop();
            MAP_UNDO.put_geometries(MAP_UNDO.current_state);
        }

        MAP_UNDO.enable_undo_button(MAP_UNDO.undo_stack.length > 0);
        MAP_UNDO.undoing = false;
    }
};

MAP_UNDO.enable_undo_button = function(enable) {
    document.getElementById('map-button-undo').disabled = !enable;
};

MAP_UNDO.get_geometries = function() {
    var geojson = new ol.format.GeoJSON();
    var features = MAP_CONFIG.draw_source.getFeatures();

    var options = {
        dataProjection: 'EPSG:27700',
        featureProjection: 'EPSG:27700'
    }

    var features_json = geojson.writeFeatures(features, options);
    return features_json;
};

MAP_UNDO.put_geometries = function(geometry) {
    var options = {
        dataProjection: 'EPSG:27700',
        featureProjection: 'EPSG:27700'
    };

    MAP_CONFIG.draw_source.clear();
    var features = new ol.format.GeoJSON().readFeatures(geometry, options);

    MAP_CONFIG.draw_source.addFeatures(features);
};
