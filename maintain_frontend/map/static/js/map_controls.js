/*global document, ol, draw_layer_styles, MAP_UNDO, MAP_CONFIG, $, map, MASTER_MAP_VECTOR_LAYER*/

var MAP_CONTROLS = {}

MAP_CONTROLS.current_interaction = null;
MAP_CONTROLS.current_style = draw_layer_styles.NONE;
// Used to generate IDs for newly created features
MAP_CONTROLS.feature_id = 0;

// Toolbar Of Available Map Controls
MAP_CONTROLS.Controls = function(controls) {
    var container = document.createElement('div');
    var noOfControls = controls.length;

    container.id = MAP_CONFIG.draw_control_id;
    container.className = "ol-control";

    for (i = 0; i < noOfControls; i++) {
        container.appendChild(controls[i]);
    }

    ol.control.Control.call(this, {
        element: container
    });
};

ol.inherits(MAP_CONTROLS.Controls, ol.control.Control);

MAP_CONTROLS.undo_button = function() {
    var button = document.createElement('button');
    button.setAttribute('id', 'map-button-undo');
    button.setAttribute('class', 'map-button-undo');
    button.setAttribute('title', 'Undo last action');
    button.disabled = true;

    var span = document.createElement('span');
    span.setAttribute('class', 'visually-hidden');
    span.textContent = 'Undo most recent action';
    button.appendChild(span);

    var handleUndo = function() {
        MAP_UNDO.undo();
    };

    button.addEventListener('click', handleUndo, false);
    return button;
}

// Draw Point Button
MAP_CONTROLS.point_button = function() {
    var button = document.createElement('button');
    button.setAttribute("id", "map-button-point");
    button.setAttribute("class", "map-button-point");
    button.setAttribute("title", "Point");
    var span = document.createElement("span");
    span.setAttribute("class", "visually-hidden");
    span.textContent = "Draw points";
    button.appendChild(span);

    var handlePoint = function() {
        MAP_CONTROLS.add_draw_interaction("Point", button);
    };

    button.addEventListener('click', handlePoint, false);
    return button
};

// Draw Line Button
MAP_CONTROLS.line_button = function() {
    var button = document.createElement('button');
    button.setAttribute("id", "map-button-line");
    button.setAttribute("class", "map-button-line");
    button.setAttribute("title", "Line");
    var span = document.createElement("span");
    span.setAttribute("class", "visually-hidden");
    span.textContent = "Draw lines";
    button.appendChild(span);

    var handleLine = function() {
        MAP_CONTROLS.add_draw_interaction("LineString", button);
    };

    button.addEventListener('click', handleLine, false);
    return button
};

// Draw Polygon Button
MAP_CONTROLS.polygon_button = function() {
    var button = document.createElement('button');
    button.setAttribute("id", "map-button-polygon");
    button.setAttribute("class", "map-button-polygon");
    button.setAttribute("title", "Polygon");
    var span = document.createElement("span");
    span.setAttribute("class", "visually-hidden");
    span.textContent = "Draw polygon";
    button.appendChild(span);

    var handlePolygon = function() {
        MAP_CONTROLS.add_draw_interaction("Polygon", button);
    };

    button.addEventListener('click', handlePolygon, false);
    return button
};

// Edit Features Button
MAP_CONTROLS.edit_button = function() {
    var button = document.createElement('button');
    button.setAttribute("id", "map-button-edit");
    button.setAttribute("class", "map-button-edit");
    button.setAttribute("title", "Edit feature");
    button.disabled = true;
    var span = document.createElement("span");
    span.setAttribute("class", "visually-hidden");
    span.textContent = "Edit features";
    button.appendChild(span);

    var handleEdit = function() {
        map.removeInteraction(MAP_CONTROLS.current_interaction);
        var toggled_on = MAP_CONTROLS.toggle_button(button);

        if (toggled_on) {
            MAP_CONTROLS.toggle_draw_layer_style(draw_layer_styles.EDIT);

            MAP_CONTROLS.current_interaction = new ol.interaction.Modify({
                features: MAP_CONFIG.draw_features,
                style: draw_layer_styles.style[draw_layer_styles.EDIT]
            });

            map.addInteraction(MAP_CONTROLS.current_interaction);
            $("#map-button-edit").trigger("edit:toggled");
            if (MAP_CONTROLS.vectorControls.snap_to_enabled) {
                map.addInteraction(snap_to_interaction)
            }

            MAP_CONTROLS.current_interaction.on('modifystart', function(event) {
                MAP_UNDO.clear_undo_stack();
            });

            MAP_CONTROLS.current_interaction.on('modifyend', function(event) {
                MAP_UNDO.update_current_state();
            });
        } else {
            MAP_CONTROLS.toggle_draw_layer_style(draw_layer_styles.NONE);
        }
    };

    button.addEventListener('click', handleEdit, false);

    return button
};

// Remove Features Button
MAP_CONTROLS.remove_button = function() {
    var button = document.createElement('button');
    button.setAttribute("id", "map-button-remove");
    button.setAttribute("class", "map-button-remove");
    button.setAttribute("title", "Remove one");
    button.disabled = true;
    var span = document.createElement("span");
    span.setAttribute("class", "visually-hidden");
    span.textContent = "Remove single features";
    button.appendChild(span);

    var handleRemove = function() {
        map.removeInteraction(MAP_CONTROLS.current_interaction);
        var toggled_on = MAP_CONTROLS.toggle_button(button);

        if (toggled_on) {
            MAP_CONTROLS.toggle_draw_layer_style(draw_layer_styles.REMOVE);

            MAP_CONTROLS.current_interaction = new ol.interaction.Select({
                layers: [MAP_CONFIG.draw_layer]
            });

            MAP_CONTROLS.current_interaction.getFeatures().on('add', function (event) {
                var feature_id = event.element.getProperties().id;

                MAP_CONTROLS.remove_selected_feature(feature_id);
                MAP_CONTROLS.current_interaction.getFeatures().clear();
            });

            map.addInteraction(MAP_CONTROLS.current_interaction)
        }
    };

    button.addEventListener('click', handleRemove, false);

    return button
};

MAP_CONTROLS.remove_all_button = function() {
    var button = document.createElement('button');
    button.setAttribute("id", "map-button-remove-all");
    button.setAttribute("class", "map-button-remove-all");
    button.setAttribute("title", "Remove all");
    button.disabled = true;
    var span = document.createElement("span");
    span.setAttribute("class", "visually-hidden");
    span.textContent = "Remove all features";
    button.appendChild(span);

    var handleRemoveAll = function() {
        MAP_UNDO.store_state();

        map.removeInteraction(MAP_CONTROLS.current_interaction);
        $('.active-control').removeClass('active-control');

        MAP_CONTROLS.toggle_draw_layer_style(draw_layer_styles.NONE)
        MAP_CONFIG.draw_source.clear();


    };

    button.addEventListener('click', handleRemoveAll, false);

    return button
};

// Toggle/Untoggle Control
MAP_CONTROLS.toggle_button = function(button) {
    var jbutton = $(button)
    var is_active_control = jbutton.hasClass('active-control');

    if (is_active_control) {
        jbutton.removeClass('active-control');
        MAP_CONTROLS.current_interaction = null;
        return false
    } else {
        $('.active-control').removeClass('active-control');
        jbutton.addClass('active-control')
        return true
    }
};

// Remove Drawn Feature
MAP_CONTROLS.remove_selected_feature = function(id) {
    MAP_UNDO.store_state();

    var features = MAP_CONFIG.draw_source.getFeatures();
    var feature = $.grep(features, function(feature) { return feature.getProperties().id == id });
    MAP_CONFIG.draw_source.removeFeature(feature[0])


};

// Add Draw Interactions
MAP_CONTROLS.add_draw_interaction = function(type, button) {
    // Remove the previous interaction
    map.removeInteraction(MAP_CONTROLS.current_interaction);
    // Toggle the draw control as needed
    var toggled_on = MAP_CONTROLS.toggle_button(button);

    if (toggled_on) {
        MAP_CONTROLS.toggle_draw_layer_style(draw_layer_styles.DRAW);

        MAP_CONTROLS.current_interaction = new ol.interaction.Draw({
            features: MAP_CONFIG.draw_features,
            type: type,
            style: draw_layer_styles.style[draw_layer_styles.DRAW],
            geometryFunction: function(coords, geometry) {
                /* Annoying callback to enable/disable the undo button and prevent
                   calls to removeLastPoint when there's no points left to undo */
                if(type==="LineString") {
                    if(!geometry) {
                        geometry = new ol.geom.LineString(null);
                    }
                    geometry.setCoordinates(coords);
                    MAP_UNDO.enable_undo_button(coords.length > 1);
                } else if(type === "Point") {
                    if(!geometry) {
                        geometry = new ol.geom.Point(null);
                    }
                    geometry.setCoordinates(coords);
                } else if(type === "Polygon") {
                    if(!geometry) {
                        geometry = new ol.geom.Polygon(null);
                    }
                    geometry.setCoordinates([coords[0].concat([coords[0][0]])]);
                    MAP_UNDO.enable_undo_button(coords[0].length > 1);
                }

                return geometry;
            }
        });

        MAP_CONTROLS.current_interaction.on('drawend', function (event) {
            event.feature.setProperties({
                'id': Date.now()
            });
            MAP_UNDO.clear_undo_stack();
        });

        map.addInteraction(MAP_CONTROLS.current_interaction);
        if (MAP_CONTROLS.vectorControls.snap_to_enabled) {
            map.addInteraction(snap_to_interaction)
        }
    }
};

// Toggle Feature Styles on draw layer for current style
MAP_CONTROLS.toggle_draw_layer_style = function(style) {
    MAP_CONTROLS.current_style = style
    MAP_CONFIG.draw_layer.setStyle(draw_layer_styles.style[style])
}

// Mastermap vector controls
MAP_CONTROLS.vectorControls = {}

MAP_CONTROLS.vectorControls.disableOverride = false;
MAP_CONTROLS.vectorControls.snap_to_enabled = false;
MAP_CONTROLS.vectorControls.copy_enabled = false;

// Enables the mm vector buttons
MAP_CONTROLS.vectorControls.enableControls = function() {
    var jbuttons = [$('#map-button-snap-to'), $('#map-button-copy')];
    for (var i = 0; i < jbuttons.length; i++) {
        jbuttons[i].removeClass('map-button-disabled');
        jbuttons[i].prop('disabled', false)
    }
};

// Disables the mm vector buttons
MAP_CONTROLS.vectorControls.disable_buttons = function() {
    var jbuttons = [$('#map-button-snap-to'), $('#map-button-copy')];
    for (var i = 0; i < jbuttons.length; i++) {
        jbuttons[i].addClass("map-button-disabled")
        jbuttons[i].prop('disabled', true)
    }
};

// Disables the vector buttons and snap to interaction
MAP_CONTROLS.vectorControls.disableControls = function() {
    MASTER_MAP_VECTOR_LAYER.disable()
    SNAP_TO_VECTOR_LAYER.disable()
    MAP_CONTROLS.vectorControls.disable_buttons()
    MAP_CONTROLS.vectorControls.snap_to_enabled = false
    MAP_CONTROLS.vectorControls.copy_enabled = false;
    $('#map-button-snap-to').removeClass('active-mode');
    $('#map-button-copy').removeClass('active-control');
    map.removeInteraction(snap_to_interaction)
};

var snap_to_interaction = new ol.interaction.Snap({
    source: SNAP_TO_VECTOR_LAYER.layer.getSource(),
    edge: true,
    vertex: true,
    pixelTolerance: 7.5
});

MAP_CONTROLS.snap_to = function() {
    var button = document.createElement('button');
    button.id = 'map-button-snap-to'
    button.disabled = true
    button.setAttribute("class", "map-button-snap-to map-button-disabled")
    button.setAttribute("title", "Snap to")
    var span = document.createElement("span");
    span.setAttribute("class", "visually-hidden");
    span.textContent = "Snap to features";
    button.appendChild(span);

    var handleSnapTo = function () {
        if (MAP_CONTROLS.vectorControls.snap_to_enabled) {
            // Disable the snap to interaction and vector layer, but not the snap to button
            // Don't disable vector layer if copy active
            if (!MAP_CONTROLS.vectorControls.copy_enabled) {
                SNAP_TO_VECTOR_LAYER.disable()
            }
            map.removeInteraction(snap_to_interaction)
            MAP_CONTROLS.vectorControls.snap_to_enabled = false
            $('#map-button-snap-to').removeClass('active-mode')
        } else {
            // Enable the snap to interaction and vector layer
            SNAP_TO_VECTOR_LAYER.enable()
            map.addInteraction(snap_to_interaction)
            MAP_CONTROLS.vectorControls.snap_to_enabled = true
            $('#map-button-snap-to').addClass("active-mode")
        }
    }

    button.addEventListener('click', handleSnapTo, false);
    return button;
};

MAP_CONTROLS.copy_button = function() {
    var button = document.createElement('button');
    button.setAttribute("id", "map-button-copy");
    button.setAttribute("class", "map-button-copy map-button-disabled");
    button.setAttribute("title", "Copy basemap feature");
    button.disabled = true
    var span = document.createElement("span");
    span.setAttribute("class", "visually-hidden");
    span.textContent = "Copy features from basemap";
    button.appendChild(span);

    var handleCopy = function() {
        map.removeInteraction(MAP_CONTROLS.current_interaction);
        var toggled_on = MAP_CONTROLS.toggle_button(button);

        if (toggled_on) {
            MASTER_MAP_VECTOR_LAYER.enable()
            MAP_CONTROLS.toggle_draw_layer_style(draw_layer_styles.DRAW);

            MAP_CONTROLS.current_interaction = new ol.interaction.Select({
                layers: [MASTER_MAP_VECTOR_LAYER.layer],
                style: draw_layer_styles.style[draw_layer_styles.DRAW]
            });

            MAP_CONTROLS.current_interaction.getFeatures().on('add', function (event) {
                MAP_UNDO.clear_undo_stack();
                feature = event.target.item(0);
                if (feature) {
                    geometry = feature.getGeometry();
                    //Convert multi polygons to features
                    if (geometry instanceof ol.geom.MultiPolygon) {
                        polygons = geometry.getPolygons()
                        for (var j = 0; j < polygons.length; j++) {
                            poly_feature = new ol.Feature({
                                geometry: polygons[j]
                            });
                            poly_feature.setProperties({
                                'id': Date.now()
                            });
                            MAP_CONFIG.draw_source.addFeature(poly_feature);
                        }
                    }
                    else {
                        new_feature = new ol.Feature({
                            geometry: geometry
                        });
                        new_feature.setProperties({
                            'id': Date.now()
                        });
                        MAP_CONFIG.draw_source.addFeature(new_feature);
                    }
                }
            });

            MAP_CONTROLS.vectorControls.copy_enabled = true;
            map.addInteraction(MAP_CONTROLS.current_interaction)
        }
        else if(!MAP_CONTROLS.vectorControls.snap_to_enabled) {
            MAP_CONTROLS.vectorControls.copy_enabled = false;
            MASTER_MAP_VECTOR_LAYER.disable()
        }
    };

    button.addEventListener('click', handleCopy, false);

    return button;
};

MAP_CONTROLS.enableControls = function(enable) {
    MAP_CONTROLS.enableButton('.map-button-edit', enable);
    MAP_CONTROLS.enableButton('.map-button-remove', enable);
    MAP_CONTROLS.enableButton('.map-button-remove-all', enable);
    MAP_CONTROLS.enableButton('#continue', enable);
};

MAP_CONTROLS.enableButton = function(selector, enable) {
    $(selector).prop('disabled', !enable);
};

MAP_CONTROLS.removeActiveControl = function() {
    map.removeInteraction(MAP_CONTROLS.current_interaction);
    $('.active-control').removeClass('active-control');
    MAP_CONTROLS.toggle_draw_layer_style(draw_layer_styles.NONE)
};
