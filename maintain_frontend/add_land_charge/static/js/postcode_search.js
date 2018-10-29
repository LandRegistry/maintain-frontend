/* global $, ol, map, $SCRIPT_ROOT */
var postcodeSearch = {
    viewModel: null,

    init: function() {
        postcodeSearch.viewModel = new postcodeSearch.ViewModel();
        ko.applyBindings(postcodeSearch.viewModel);
    },

    ViewModel: function() {
        var self = this;

        self.errorMessages = ko.observableArray();
        self.addresses = ko.observableArray();
        self.noAddressesFound = ko.observable();
        self.selectedAddress = ko.observable();

        self.searchAddresses = function (data, event) {
            if (event.type === "click" || event.keyCode === 13) {
                $.getJSON($SCRIPT_ROOT + '/_search/postcode', {
                    postcode: $('#search_term').val()
                })

                .done(function(response) {
                    if (response.status === 'success') {
                        self.errorMessages([]);
                        self.addresses([]);
                        var responseAddresses = response.data;
                        for (var i = 0; i < responseAddresses.length; i++) {
                            self.addresses.push(new postcodeSearch.Address(responseAddresses[i]));
                        }
                    } else {
                        self.clear();
                        self.addErrorMessage('#search_term', response.search_message, response.inline_message);
                    }
                })

                .fail(function(response) {
                    if (response.status === 403) {
                        window.location.replace('/logout')
                    } else {
                        window.location.replace('/error')
                    }
                })
            } else {
                // Keypress binding prevents typing other characters. Allowing default event.
                return true;
            }
        };

        self.selectAddress = function (address) {
            self.clear();
            self.selectedAddress(address);
        };

        self.clear = function () {
            self.addresses([]);
            self.errorMessages([]);
        };

        self.addErrorMessage = function(field, message, inline) {
            self.errorMessages.push(new postcodeSearch.ErrorMessage(field, message, inline))
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

    },

    Address: function (addressObj) {
        var self = this;

        self.address = addressObj["address"];
        self.line_1 = addressObj["line_1"];
        self.line_2 = addressObj["line_2"];
        self.line_3 = addressObj["line_3"];
        self.line_4 = addressObj["line_4"];
        self.line_5 = addressObj["line_5"];
        self.line_6 = addressObj["line_6"];
        self.postcode = addressObj["postcode"];
        self.geometry = addressObj["geometry"];
        self.uprn = addressObj["uprn"];
    },

    ErrorMessage: function(field, message, inline) {
        var self = this;

        self.field = field;
        self.message = message;
        self.inline = inline;
    }
};
