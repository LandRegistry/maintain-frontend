/* global $, ol, map, $SCRIPT_ROOT, MAP_HELPERS, MAP_CONTROLS */
var addLocation = {
    addressMarker: null,
    viewModel: null,

    init: function (staticContentPath) {
        // Add Map Controls
        var controls = new MAP_CONTROLS.Controls([
            MAP_CONTROLS.polygon_button(),
            MAP_CONTROLS.point_button(),
            MAP_CONTROLS.line_button(),
            MAP_CONTROLS.edit_button(),
            MAP_CONTROLS.copy_button(),
            MAP_CONTROLS.remove_button(),
            MAP_CONTROLS.remove_all_button(),
            MAP_CONTROLS.undo_button(),
            MAP_CONTROLS.snap_to()
        ]);

        MAP_HELPERS.init_controls(map, controls);

        addLocation.addressMarker = new AddressMarker(staticContentPath);
        map.addLayer(addLocation.addressMarker.addressMarkerLayer);

        addLocation.viewModel = new addLocation.ViewModel();
        ko.applyBindings(addLocation.viewModel);
    },

    ViewModel: function () {
        var self = this;

        self.errorMessages = ko.observableArray();
        self.extentCount = ko.observable("0 extents");
        self.extentTypesText = ko.observable(" (polygons, points or lines)");
        self.addresses = ko.observableArray();
        self.noAddressesFound = ko.observable();
        self.selectedAddress = ko.observable();

        self.flexSelectAddress = function (address) {
            if (address.address_type === "property") {
                self.addresses([]);
                if (document.getElementById("search_term")) {
                    document.getElementById("search_term").value = "";
                }
                addLocation.zoomToLocation([address.geometry["coordinates"]]);
                self.selectedAddress(address);
                addLocation.addressMarker.markAddressLocation(address.geometry);
            } else if (address.address_type === "street") {
                if (document.getElementById("search_term")) {
                    document.getElementById("search_term").value = "";
                }
                self.usrnSearch(address.usrn);
                addLocation.zoomToLocation(address.geometry["coordinates"]);
                self.selectedAddress(address);
            }
        };

        self.flexSearchAddresses = function (data, event) {
            if (event.type === "click" || event.keyCode === 13) {
                $.getJSON($SCRIPT_ROOT + '/_search/text/v2.0', {
                    search_term: $('#search_term').val()
                })

                .done(function(response) {
                    if (response.status === 'success') {
                        self.clear();
                        var responseAddresses = response.data;
                        if (responseAddresses.length > 0) {
                            for (var i = 0; i < responseAddresses.length; i++) {
                                self.addresses.push(new addLocation.Address(responseAddresses[i]));
                            }
                        } else {
                            self.addErrorMessage('#search_term', "Enter a valid location", null);
                        }
                    } else {
                        self.clear();
                        self.addErrorMessage('#search_term', response.search_message, null);
                    }
                })

                .fail(function(response) {
                    if (response.status === 403) {
                        window.location.replace('/logout')
                    } else {
                        window.location.replace('/error')
                    }
                })
            }
        };

        self.usrnSearch = function(usrn) {
            $.getJSON($SCRIPT_ROOT + '/_search/usrn', {
                search_term: usrn
            })

            .done(function(response) {
                if (response.status === 'success') {
                    self.clear();
                    var responseAddresses = response.data;
                    if (responseAddresses.length > 0) {
                        for (var i = 0; i < responseAddresses.length; i++) {
                            self.addresses.push(new addLocation.Address(responseAddresses[i]));
                        }
                    } else {
                        self.addErrorMessage('#search_term', "Enter a valid location", null);
                    }
                } else {
                    self.clear();
                    self.addErrorMessage('#search_term', response.search_message, null);
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

        self.clear = function() {
            self.errorMessages([]);
            self.addresses([]);
        };

        self.showSelectedAddress = ko.computed(function(){
            return self.selectedAddress();
        });

        self.addErrorMessage = function(field, message, inline) {
            self.errorMessages.push(new addLocation.ErrorMessage(field, message, inline))
        };

        self.errorsForField = function(field) {
            var errors = ko.utils.arrayFilter(self.errorMessages(), function(error) {
                return error.field.toLowerCase() ===  field.toLowerCase();
            });

            if(errors.length > 0) {
                return errors
            }

            return null;
        };

        self.countFeatures = function() {
            return MAP_CONFIG.draw_features.getLength();
        };

        MAP_CONFIG.draw_features.on('change:length', function() {
            var count = self.countFeatures();
            MAP_CONTROLS.enableControls(count !== 0);
            var countText = count + " extents";
            var typesText = " (polygons, points or lines)";
            if (count === 1) {
                countText = count + " extent";
                typesText = " (polygon, point or line)"
            }
            self.extentCount(countText);
            self.extentTypesText(typesText);
        });
    },

    Address: function (addressObj) {
        var self = this;

        self.address = addressObj["address"];
        self.address_type = addressObj["address_type"];
        self.line_1 = addressObj["line_1"];
        self.line_2 = addressObj["line_2"];
        self.line_3 = addressObj["line_3"];
        self.line_4 = addressObj["line_4"];
        self.line_5 = addressObj["line_5"];
        self.line_6 = addressObj["line_6"];
        self.postcode = addressObj["postcode"];
        self.geometry = addressObj["geometry"];
        self.uprn = addressObj["uprn"];
        self.usrn = addressObj["usrn"];
    },

    ErrorMessage: function(field, message, inline) {
        var self = this;

        self.field = field;
        self.message = message;
        self.inline = inline;
    },

    zoomToLocation: function (coordinates) {
        var extent = new ol.extent.boundingExtent(coordinates)
        map.getView().fit(extent, {duration: 1000, maxZoom: 15})
    }
};
