/* global $, map, ol, MAP_HELPERS  */
var search = search || {}
var PERMISSIONS = null;

(function (search) {
    search._scriptRoot = null;

    // Open Layers Local Land Charge Display Layer
    search.llcSource = new ol.source.Vector({});
    search.llcLayer = new ol.layer.Vector({
        source: search.llcSource,
        zIndex: MAP_CONFIG.llc_layer_zindex
    });

    // Open Layers Highlighted Charge Display Layer
    search.highlightedSource = new ol.source.Vector({});
    search.highlightedLayer = new ol.layer.Vector({
        source: search.highlightedSource,
        zIndex: MAP_CONFIG.highlighted_charge_layer_zindex
    });

    // Activates knockout.js
    search.searchViewModel = new search.SearchViewModel();

    search.addressMarker = null;

    search.init = function(permissions, staticContentPath, scriptRoot) {
        PERMISSIONS = permissions;
        search._scriptRoot = scriptRoot;

        $('span.icon.toggle-category').keydown(function(e) {
          if (e.keyCode == 13) {
            this.click();
          }
        });

        var controls = new MAP_CONTROLS.Controls([
            MAP_CONTROLS.polygon_button(),
            MAP_CONTROLS.edit_button(),
            MAP_CONTROLS.copy_button(),
            MAP_CONTROLS.remove_all_button(),
            MAP_CONTROLS.undo_button(),
            MAP_CONTROLS.snap_to()
        ]);

        MAP_HELPERS.init_controls(map, controls);

        // Add New Layer to Open Layers for LLC
        map.addLayer(search.llcLayer);
        map.addLayer(search.highlightedLayer);

        search.addressMarker = new AddressMarker(staticContentPath);
        map.addLayer(search.addressMarker.addressMarkerLayer);

        ko.applyBindings(search.searchViewModel);
    };

    search.zoomToLocation = function (coordinates) {
        var extent = new ol.extent.boundingExtent(coordinates)
        map.getView().fit(extent, {duration: 1000, maxZoom: 15})
    };


    search.chargesInArea = function(geometry) {
        $.ajax({
            type : "POST",
            url: search._scriptRoot + '/_search/local_land_charges',
            data: JSON.stringify(geometry.getCoordinates()),
            contentType: 'application/json'
        })

        .done(function(localLandCharges) {
            if (localLandCharges.status === 200) {
                search.searchViewModel.populateCharges(localLandCharges.data);
                chargeLayer.drawChargesInCategories(search.searchViewModel.categories())
            } else if (localLandCharges.status === 404) {
                search.searchViewModel.noChargesFound(true);
                search.searchViewModel.resultLimitExceeded(false);
                search.searchViewModel.resetCategories();
                search.searchViewModel.resetResults();
                search.llcSource.clear();
            } else if (localLandCharges.status === 507) {
                search.searchViewModel.noChargesFound(false);
                search.searchViewModel.resultLimitExceeded(true);
                search.searchViewModel.resetCategories();
                search.searchViewModel.resetResults();
                search.llcSource.clear();
            } else {
                window.location.replace('/error');
            }
        })

        .fail(function(response) {
            if (response.status === 403) {
                window.location.replace('/logout')
            } else {
                window.location.replace('/error')
            }
        })
    };

    search.search_previous_extent = function(searchExtent) {
        if(searchExtent) {
            searchExtent = searchExtent.replace(/&#39;/g, "\"");
            searchExtent = searchExtent.replace(/&#34;/g, "\"");
            try {
                var options = {
                    dataProjection: 'EPSG:27700',
                    featureProjection: 'EPSG:27700'
                };

                var features = new ol.format.GeoJSON().readFeatures(searchExtent, options);

                MAP_CONFIG.draw_source.addFeatures(features);
                MAP_CONFIG.draw_layer.setStyle(draw_layer_styles.style[draw_layer_styles.DRAW])

                var zoomExtent = features[0].getGeometry().getExtent();
                map.getView().fit(zoomExtent);
            } catch (e) {
                window.location.replace('/error');
            }
        }
    };

    search.scrollTo = function(container, child) {
        container.scrollTop(child.offset().top - container.offset().top + container.scrollTop());
    };

    ko.bindingHandlers.trimText = {
        init: function (element, valueAccessor) {
            var trimmedText = ko.computed(function () {
                var untrimmedText = ko.utils.unwrapObservable(valueAccessor());
                var maxLength = 35;

                var text = untrimmedText.length > maxLength ? untrimmedText.substring(0, maxLength - 1)
                    + '...' : untrimmedText;
                return text;
            });

            ko.applyBindingsToNode(element, {
                text: trimmedText
            });
        }
    };

})(search);
