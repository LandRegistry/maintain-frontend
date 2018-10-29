// Styles for LLC Layer
llc_layer_styles = {
    Polygon: "Polygon",

    // Non-highlighted styles for llc_layer features
    standard_style: {
        "Point": new ol.style.Style({
            image: new ol.style.Circle({
                radius: 7,
                stroke: new ol.style.Stroke({
                    color: '#0658e5',
                    width: 1
                }),
                fill: new ol.style.Fill({
                    color: [255, 255, 255, 1]
                })
            })
        }),
        "Polygon": new ol.style.Style({
            fill: new ol.style.Fill({
                color: [255, 255, 255, 0.7]
            }),
            stroke: new ol.style.Stroke({
                color: '#0658e5',
                width: 1
            })
        }),
        "LineString": new ol.style.Style({
            fill: new ol.style.Fill({
                color: [255, 255, 255, 0.7]
            }),
            stroke: new ol.style.Stroke({
                color: '#0658e5',
                width: 1
            })
        })
    },
    // Highlighted styles for llc_layer features
    selected_style: {
        "Point": new ol.style.Style({
            image: new ol.style.Circle({
                radius: 7,
                stroke: new ol.style.Stroke({
                    color: '#0658e5',
                    width: 1
                }),
                fill: new ol.style.Fill({
                    color: '#0658e5'
                })
            })
        }),
        "Polygon": new ol.style.Style({
            fill: new ol.style.Fill({
                color: [255, 255, 255, 0.7]
            }),
            stroke: new ol.style.Stroke({
                color: '#0658e5',
                width: 3
            })
        }),
        "LineString": new ol.style.Style({
            fill: new ol.style.Fill({
                color: [255, 255, 255, 0.7]
            }),
            stroke: new ol.style.Stroke({
                color: '#0658e5',
                width: 3
            })
        })
    },
    // Highlighted styles for llc_layer features
    hidden: {
        "Point": new ol.style.Style({
            image: new ol.style.Circle({
                radius: 7,
                stroke: new ol.style.Stroke({
                    color: [255, 255, 255, 0]
                }),
                fill: new ol.style.Fill({
                    color: [255, 255, 255, 0]
                })
            })
        }),
        "Polygon": new ol.style.Style({
            fill: new ol.style.Fill({
                color: [255, 255, 255, 0]
            }),
            stroke: new ol.style.Stroke({
                color: [255, 255, 255, 0]
            })
        }),
        "LineString": new ol.style.Style({
            fill: new ol.style.Fill({
                color: [255, 255, 255, 0]
            }),
            stroke: new ol.style.Stroke({
                color: [255, 255, 255, 0]
            })
        })
    }
}

draw_layer_styles = {
    // Draw Interactions
    DRAW: 0,
    // Edit Interactions
    EDIT: 1,
    // Remove Interactions
    REMOVE: 2,
    // No Interactions Toggled
    NONE: 3,
    // Associated Feature Styles for mode
    style: {
        0: new ol.style.Style({
            fill: new ol.style.Fill({
                color: [255, 255, 255, 0.4]
            }),
            stroke: new ol.style.Stroke({
                color: '#0658e5',
                width: 2,
                lineDash: [1, 5]
            }),
            image: new ol.style.Circle({
                radius: 5,
                fill: new ol.style.Fill({
                    color: '#0658e5'
                })
            })
        }),
        1: new ol.style.Style({
            fill: new ol.style.Fill({
                color: [255, 255, 255, 0.6]
            }),
            stroke: new ol.style.Stroke({
                color: '#ffcc33',
                width: 2,
                lineDash: [1, 5]
            }),
            image: new ol.style.Circle({
                radius: 5,
                fill: new ol.style.Fill({
                    color: '#ffcc33'
                })
            })
        }),
        2: new ol.style.Style({
            stroke: new ol.style.Stroke({
                color: [255,0,0,0.4],
                width: 2,
                lineDash: [1, 5]
            }),
            fill: new ol.style.Fill({
                color: [255,0,0,0.2]
            }),
            image: new ol.style.Circle({
                radius: 5,
                fill: new ol.style.Fill({
                    color: '#ff0000'
                })
            }),
            zIndex: 1
        }),
        3: new ol.style.Style({
            fill: new ol.style.Fill({
                color: [255, 255, 255, 0.4]
            }),
            stroke: new ol.style.Stroke({
                color: '#0658e5',
                width: 2,
                lineDash: [1, 5]
            }),
            image: new ol.style.Circle({
                radius: 5,
                fill: new ol.style.Fill({
                    color: '#0658e5'
                })
            })
        })
    }
}
