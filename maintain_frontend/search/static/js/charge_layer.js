var chargeLayer = {};

chargeLayer.drawChargesInCategories = function (categories) {
    search.llcSource.clear()
    var charges = categories.map(function(category) {
            return category.charges()
    });
    charges = charges.concat.apply([], charges);
    chargeLayer.addChargesToSource(charges);
};

chargeLayer.hideFeatures = function (charges) {
    var features = search.llcSource.getFeatures().filter(function(feature) {
        var charge = feature.getProperties().charge;
        return charges.indexOf(charge) >= 0;
    });
    featureHelpers.setStyleForFeatures(features, llc_layer_styles.hidden)
};

chargeLayer.showFeatures = function (charges) {
    var features = search.llcSource.getFeatures().filter(function(feature) {
        var charge = feature.getProperties().charge;
        return charges.indexOf(charge) >= 0;
    });
    if (features.length === 0) {
        chargeLayer.addChargesToSource(charges);
        return;
    }
    featureHelpers.setStyleForFeatures(features, llc_layer_styles.standard_style)
};

chargeLayer.addChargesToSource = function (charges) {
    var features = featureHelpers.buildFeaturesForCharges(charges);

    features.forEach(function(feature) {
        var checked = feature.getProperties().charge.category.checked();
        var style = (checked ? llc_layer_styles.standard_style : llc_layer_styles.hidden);
        featureHelpers.setStyleForFeature(feature, style);
        search.llcSource.addFeature(feature);
    });
};
