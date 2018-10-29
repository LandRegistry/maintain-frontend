var search = search || {};

// Represent a row in the address result set
search.Address = function(addressObj) {
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
};

// Represent a row in the Category Accordion result set
search.Charge = function(chargeObj) {
    var self = this;

    self.id = chargeObj["display_id"];
    self.geometry = chargeObj["geometry"];
    self.type = chargeObj["item"]["charge-type"];
    self.reference = chargeObj["item"]["further-information-reference"] || "Not provided";
    self.category = undefined;

    if ('charge-address' in chargeObj['item']) {
        self.chargeGeographicDescription = chargeObj['item']['charge-address']['line-1'];
    } else {
        self.chargeGeographicDescription = chargeObj["item"]["charge-geographic-description"];
    }

    self.highlight = function() {
        $('#' + self.id).addClass('highlighted');
        var features = self.getFeatures(search.llcSource);
        featureHelpers.setStyleForFeatures(features, llc_layer_styles.selected_style);
        featureHelpers.addFeaturesToSource(features, search.highlightedSource);
    };

    self.removeHighlight = function() {
        $('#' + self.id).removeClass('highlighted');
        var features = self.getFeatures(search.highlightedSource);
        featureHelpers.removeFeaturesFromSource(features, search.highlightedSource);

        if(self.category.checked()) {
            featureHelpers.setStyleForFeatures(features, llc_layer_styles.standard_style);
        } else {
            featureHelpers.setStyleForFeatures(features, llc_layer_styles.hidden);
        }
    };

    self.getFeatures = function(source) {
        return source.getFeatures().filter(function(feature) {
            return feature.getProperties().charge.id === self.id
        });
    };
};

// Represent an Accordion for containing charges of a particular type/category
search.Category = function(name, checked) {
    var self = this;

    // True by default otherwise use provided value
    self.initialCheck = (checked === undefined || checked);
    self.name = name;
    self.expanded = false;
    self.charges = ko.observableArray();

    self.checked = ko.observable(self.initialCheck);
    self.checked.subscribe(function(isChecked) {
        if(isChecked) {
            chargeLayer.showFeatures(self.charges())
        } else {
            chargeLayer.hideFeatures(self.charges())
        }
    });

    self.clearCharges = function () {
        self.charges.removeAll();
    };

    self.resetChecked = function() {
        self.checked(self.initialCheck)
    };

    self.getChargeIds = function () {
        return self.charges().map(function(charge) {
            return charge.id
        })
    };

    self.filterId = ko.computed(function() {
        return self.name.replace(/\s+/g, '-').toLowerCase();
    });

    self.sectionId = ko.computed(function() {
        return self.name.replace(/\s+/g, '-').toLowerCase() + "-section";
    });

    self.categoryHeader = ko.computed(function() {
        return self.name + " (" + self.charges().length + ")";
    });

    self.toggleCategorySection = function(item, event) {
        var expanded = $("#" + self.sectionId()).attr("aria-expanded") == "true";
        self.expand(!expanded);
    };

    self.toggleCategoryKeyPress = function(data, e) {
        if (e.keyCode == 13) {
            self.toggleCategorySection();
        }
    };

    self.expand = function(expand) {
        $("#" + self.sectionId()).attr("aria-expanded", expand);
        self.expanded = expand;
        search.searchViewModel.updateOpenCloseAll();
    };
};

// Overall viewmodel for this screen, along with initial state
search.SearchViewModel = function() {
    var self = this;

    self.errorMessage = ko.observable();
    self.noChargesFound = ko.observable();
    self.resultLimitExceeded = ko.observable();
    self.selectedAddress = ko.observable();
    self.highlightedFeature = ko.observable();

    self.highlightedFeature.subscribe(function(newVal) {
        if (newVal) {
            var charge = newVal.getProperties().charge;
            var category = charge.category;

            var $sidebar = $("#full-screen-map-sidebar");
            var $categoryHeader = $("#" + category.sectionId() + " .accordion-section-header");

            search.scrollTo($sidebar, $categoryHeader);

            if(category.expanded) {
                var $chargeList = $("#" + category.sectionId() + " ul");
                var $chargeListItem = $('#' + charge.id);
                search.scrollTo($chargeList, $chargeListItem);
                $chargeListItem.addClass('highlighted');
            } else {
                $("#" + category.sectionId() + " .accordion-section-header").addClass('highlighted');
            }
        }
    });

    self.highlightedFeature.subscribe(function(oldVal) {
        if (oldVal) {
            var charge = oldVal.getProperties().charge;
            var category = charge.category;

            if(category.expanded) {
                $("#" + charge.id).removeClass('highlighted');
            } else {
                $("#" + category.sectionId() + " .accordion-section-header").removeClass('highlighted');
            }
        }
    }, null, "beforeChange");


    self.resetHighlightedFeature = function() {
        if(self.highlightedFeature()) {
            featureHelpers.setStyleForFeature(self.highlightedFeature(), llc_layer_styles.standard_style)
            self.highlightedFeature(undefined)
        }
    };

    self.addresses = ko.observableArray();
    self.charges = ko.observableArray();

    self.otherCategory = new search.Category("Other");
    self.categories = ko.observableArray([
        new search.Category("Planning"),
        new search.Category("Housing"),
        new search.Category("Listed building"),
        new search.Category("Financial"),
        new search.Category("Land compensation"),
        new search.Category("Light obstruction notice"),
        new search.Category("Conservation areas", false),
        new search.Category("Smoke control orders", false),
        new search.Category("Sites of special scientific interest", false),
        self.otherCategory
    ]);

    self.showSelectedAddress = ko.computed(function(){
        return self.selectedAddress() && self.charges().length == 0;
    });

    self.showDrawHelpText = ko.computed(function(){
        return !self.selectedAddress() && self.charges().length == 0;
    });

    self.populateCharges = function (charges) {
        self.reset();

        if(!(MAP_CONTROLS.current_interaction instanceof ol.interaction.Modify)) {
            self.resetCategories();
        }

        for(var i = 0; i < charges.length; i++) {
            var charge = new search.Charge(charges[i]);
            self.charges.push(charge);
        }

        self.setCategoryCharges(self.charges());
    };

    self.setCategoryCharges = function(charges) {
        self.categories().forEach(function(category) {
            category.clearCharges();
        });

        charges.forEach(function(charge) {
           var foundCategory = ko.utils.arrayFirst(self.categories(), function(category) {
               return charge.type.toLowerCase() === category.name.toLowerCase();
           });

           if (foundCategory) {
               foundCategory.charges.push(charge)
               charge.category = foundCategory
           } else {
               self.otherCategory.charges.push(charge)
               charge.category = self.otherCategory
           }
        });
    };

    self.reset = function() {
        self.noChargesFound(false);
        self.resultLimitExceeded(false);
        self.resetResults();
    };

    self.resetResults = function() {
        self.addresses.removeAll();
        self.charges.removeAll();
    };

    self.resetCategories = function() {
        self.categories().forEach(function(category) {
           category.resetChecked();
           category.clearCharges();
        });
    };

    self.clearPreviousSearch = function () {
        self.reset();
        self.resetCategories();
        self.selectedAddress(null);
        // Map Features
        search.llcSource.clear();
        MAP_CONFIG.draw_source.clear();
    };

    self.searchAddresses = function(data, event) {
        if (event.type === "click" || event.keyCode === 13) {
            $.getJSON(search._scriptRoot + '/_search/postcode', {
                postcode: $('#search-field').val()
            })

            .done(function(response) {
                self.clearPreviousSearch();
                if (response.status === 'success') {
                    self.errorMessage(null);
                    var responseAddresses = response.data;
                    for (var i = 0; i < responseAddresses.length; i++) {
                        self.addresses.push(new search.Address(responseAddresses[i]));
                    }
                } else {
                    self.errorMessage(response.search_message);
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

    self.flexSearchAddresses = function(data, event) {
        if (event.type === "click" || event.keyCode === 13) {
            self.clearPreviousSearch();

            $.getJSON(search._scriptRoot + '/_search/text/v2.0', {
                search_term: $('#search-field').val()
            })

            .done(function(response) {
                if (response.status === 'success') {
                    self.errorMessage(null);
                    var responseAddresses = response.data;
                    if (responseAddresses.length > 0) {
                        for (var i = 0; i < responseAddresses.length; i++) {
                            self.addresses.push(new search.Address(responseAddresses[i]));
                        }
                    } else {
                        self.errorMessage("Enter a valid location");
                    }
                } else {
                    self.errorMessage(response.search_message);
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
        self.clearPreviousSearch();

        $.getJSON(search._scriptRoot + '/_search/usrn', {
            search_term: usrn
        })

        .done(function(response) {
            if (response.status === 'success') {
                self.errorMessage(null);
                var responseAddresses = response.data;
                if (responseAddresses.length > 0) {
                    for (var i = 0; i < responseAddresses.length; i++) {
                        self.addresses.push(new search.Address(responseAddresses[i]));
                    }
                } else {
                    self.errorMessage("Enter a valid location");
                }
            } else {
                self.errorMessage(response.search_message);
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

    self.selectAddress = function(address) {
        self.addresses([]);
        search.addressMarker.markAddressLocation(address.geometry);
        search.zoomToLocation([address.geometry["coordinates"]]);
        self.selectedAddress(address.address)
    };

    self.flexSelectAddress = function(address) {
        if (address.address_type === "property") {
            self.addresses([]);
            if (document.getElementById("search-field")) {
                document.getElementById("search-field").value = "";
            }
            search.addressMarker.markAddressLocation(address.geometry);
            search.zoomToLocation([address.geometry["coordinates"]]);
            self.selectedAddress(address.address)
        } else if (address.address_type === "street") {
            if (document.getElementById("search-field")) {
                document.getElementById("search-field").value = "";
            }
            self.usrnSearch(address.usrn);
            search.zoomToLocation(address.geometry["coordinates"]);
            self.selectedAddress(address.address)
        }
    };

    // Expand Collapse Master Controls

    self.toggleFilterSection = function(item, event) {
        var expanded = $("#filter-accordion .accordion-section").attr("aria-expanded") == "true"
        $("#filter-accordion .accordion-section").attr("aria-expanded", !expanded)
    };

    self.toggleFilterKeyPress = function(data, e) {
        if (e.keyCode == 13) {
            self.toggleFilterSection()
        }
    }

    self.selectAllFilters = function() {
        self.categories().forEach(function(category) {
            category.checked(true)
        });
    };

    self.deselectAllFilters = function() {
        self.categories().forEach(function(category) {
            category.checked(false)
        });
    };

    self.openCloseAll = function(item, event) {
        var expanded = !($(event.target).attr('aria-expanded') == 'true')

        self.categories().forEach(function(category) {
            category.expand(expanded);
        });

        var new_button_text = expanded ? "Close all" : "Open all";
        $(event.target).attr('aria-expanded', expanded);
        $(event.target).text(new_button_text);
    };

    self.updateOpenCloseAll = function() {
        var visibleCategories = ko.utils.arrayFilter(self.categories(), function(category) {
            return category.charges().length
        });

        var allExpanded = visibleCategories.every(function(category) {
            return category.expanded
        });

        var new_button_text = allExpanded ? "Close all" : "Open all";
        $(".accordion-expand-all").attr('aria-expanded', allExpanded);
        $(".accordion-expand-all").text(new_button_text);
    }
};