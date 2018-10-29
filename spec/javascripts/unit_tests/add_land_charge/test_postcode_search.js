/* global describe, it, spyOn, expect, postcodeSearch, $, ko, beforeEach, addLocation */
describe('Postcode Search', function () {
  beforeEach(function () {
    ko.cleanNode($('body')[ 0 ])
    $SCRIPT_ROOT = ''
    postcodeSearch.init()
  })

  describe('searchAddresses', function () {
    describe('Successful calls', function () {
      it('I search for postcode successful address finder partial', function () {
        var response = {
          'status': 'success',
          'data': [ {
            'geometry': {
              'coordinates': [
                [ 1, 1 ]
              ]
            },
            'line_1': 'test',
            'line_2': 'test',
            'line_3': 'test',
            'line_4': 'test',
            'line_5': 'test',
            'line_6': 'test',
            'postcode': 'test',
            'uprn': 'test'
          } ]
        }

        var deferred = $.Deferred()
        deferred.resolve(response)

        spyOn($, 'getJSON').and.returnValue(deferred.promise())
        spyOn(postcodeSearch.viewModel.addresses, 'push')

        postcodeSearch.viewModel.searchAddresses(null, { 'type': 'click' })

        expect(postcodeSearch.viewModel.addresses.push).toHaveBeenCalledTimes(1)
      })
    })
  })

  describe('Failed calls', function () {
    it('I Search for invalid postcode', function () {
      var response = {
        'status': 'error',
        'search_message': 'No match found',
        'inline_message': 'Try a different postcode'
      }

      var deferred = $.Deferred()
      deferred.resolve(response)

      spyOn($, 'getJSON').and.returnValue(deferred.promise())
      spyOn(postcodeSearch.viewModel.addresses, 'push')
      spyOn(postcodeSearch.viewModel, 'addErrorMessage')

      postcodeSearch.viewModel.searchAddresses(null, { 'type': 'click' })

      expect(postcodeSearch.viewModel.addresses.push).not.toHaveBeenCalled()
      expect(postcodeSearch.viewModel.addErrorMessage).toHaveBeenCalledWith('#search_term', 'No match found', 'Try a different postcode')
    })

    it('I Search for a postcode with no data', function () {
      var response = {
        'status': 'error',
        'search_message': 'Enter a postcode',
        'inline_message': 'Search for a different postcode if the address you need is not listed.'
      }

      var deferred = $.Deferred()
      deferred.resolve(response)

      spyOn($, 'getJSON').and.returnValue(deferred.promise())
      spyOn(postcodeSearch.viewModel.addresses, 'push')
      spyOn(postcodeSearch.viewModel, 'addErrorMessage')

      postcodeSearch.viewModel.searchAddresses(null, { 'type': 'click' })

      expect(postcodeSearch.viewModel.addresses.push).not.toHaveBeenCalled()
      expect(postcodeSearch.viewModel.addErrorMessage).toHaveBeenCalledWith('#search_term', 'Enter a postcode', 'Search for a different postcode if the address you need is not listed.')
    })

    it('I select address, stores address, clears addresses and error messages', function () {
      var testAddress = new addLocation.Address({
        'geometry': {
          'coordinates': [
            [ 1, 1 ]
          ]
        },
        'line_1': 'test',
        'line_2': 'test',
        'line_3': 'test',
        'line_4': 'test',
        'line_5': 'test',
        'line_6': 'test',
        'postcode': 'test',
        'uprn': 'test'
      })

      spyOn(postcodeSearch.viewModel, 'selectedAddress')
      spyOn(postcodeSearch.viewModel, 'addresses')
      spyOn(postcodeSearch.viewModel, 'errorMessages')

      postcodeSearch.viewModel.selectAddress(testAddress)

      expect(postcodeSearch.viewModel.selectedAddress).toHaveBeenCalledWith(testAddress)
      expect(postcodeSearch.viewModel.addresses).toHaveBeenCalledWith([])
      expect(postcodeSearch.viewModel.errorMessages).toHaveBeenCalledWith([])
    })

    it('Redirects to /logout on recieving a 403 response from the AJAX call', function () {
      var deferred = $.Deferred()
      deferred.reject({
        'status': 403
      })

      spyOn($, 'getJSON').and.returnValue(deferred.promise())
      spyOn(window.location, 'replace')

      postcodeSearch.viewModel.searchAddresses(null, { 'type': 'click' })

      expect(window.location.replace).toHaveBeenCalledWith('/logout')
    })

    it('Redirects user to /error on recieving a non 403 response from the AJAX call', function () {
      var deferred = $.Deferred()
      deferred.reject({
        'status': 500
      })

      spyOn($, 'getJSON').and.returnValue(deferred.promise())
      spyOn(window.location, 'replace')

      postcodeSearch.viewModel.searchAddresses(null, { 'type': 'click' })

      expect(window.location.replace).toHaveBeenCalledWith('/error')
    })
  })
})
