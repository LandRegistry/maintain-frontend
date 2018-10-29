var featureHelpers = {};

featureHelpers.buildFeaturesForCharges = function (charges) {

    var featuresToAdd = [];

    charges.forEach(function(charge){
        charge.geometry.features.forEach(function(feature) {
            feature['properties'] = {
                'charge': charge
            };
            featuresToAdd.push(feature);
        });
    });

    var geoJson = {
        'type': 'FeatureCollection',
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:27700'
            }
        },
        'features': featuresToAdd
    };

    var options = {
        'dataProjection': 'EPSG:27700',
        'featureProjection': 'EPSG:27700'
    };

    return (new ol.format.GeoJSON()).readFeatures(geoJson, options)
};

featureHelpers.setStyleForFeature = function(feature, style) {
    feature.setStyle(style[feature.getGeometry().getType()]);
};

featureHelpers.setStyleForFeatures = function(features, style) {
    features.forEach(function(feature) {
        featureHelpers.setStyleForFeature(feature, style);
    });
};

featureHelpers.removeFeaturesFromSource = function(features, source) {
    features.forEach(function(feature) {
        source.removeFeature(feature);
    });
};

featureHelpers.addFeaturesToSource = function(features, source) {
    features.forEach(function(feature) {
        source.addFeature(feature);
    });
};
