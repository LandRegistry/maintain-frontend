/* global describe, it, spyOn, expect, $, MAP_HELPERS, addLocation, ko, beforeEach */
describe('Add map sidebar', function () {
  beforeEach(function () {
    ko.cleanNode($('body')[ 0 ])
    var attributionDiv = '<div class="ol-attribution ol-unselectable ol-control ol-uncollapsible">'
    document.body.insertAdjacentHTML('beforebegin', attributionDiv)
    $SCRIPT_ROOT = ''
    // Mock out init_controls function before calling init
    var addControlsFunc = MAP_HELPERS.init_controls
    MAP_HELPERS.init_controls = function () {}
    addLocation.init('')
    // Reset function to original
    MAP_HELPERS.init_controls = addControlsFunc
  })

  describe('searchAddresses', function () {
    describe('Successful calls', function () {
      it('I search for postcode successful in add location page', function () {
        var response = {
          'status': 'success',
          'data': [ {
            'address_type': 'property',
            'geometry': {
              'coordinates': [ 1, 1 ],
              'type': 'Point'
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
        spyOn(addLocation.viewModel.addresses, 'push')

        addLocation.viewModel.flexSearchAddresses(null, { 'type': 'click' })

        expect(addLocation.viewModel.addresses.push).toHaveBeenCalledWith(new addLocation.Address(response.data[0]))
      })
    })

    describe('Failed calls', function () {
      it('Correct error is returned for an invalid search', function () {
        var response = {
          'status': 'error',
          'search_message': 'Invalid search, please try again'
        }

        var deferred = $.Deferred()
        deferred.resolve(response)

        spyOn($, 'getJSON').and.returnValue(deferred.promise())
        spyOn(addLocation.viewModel.addresses, 'push')
        spyOn(addLocation.viewModel, 'addErrorMessage')

        addLocation.viewModel.flexSearchAddresses(null, { 'type': 'click' })

        expect(addLocation.viewModel.addresses.push).not.toHaveBeenCalled()
        expect(addLocation.viewModel.addErrorMessage).toHaveBeenCalledWith('#search_term', response.search_message, null)
      })

      it('Redirects to /logout on recieving a 403 response from the AJAX call', function () {
        var deferred = $.Deferred()
        deferred.reject({
          'status': 403
        })

        spyOn($, 'getJSON').and.returnValue(deferred.promise())
        spyOn(window.location, 'replace')

        addLocation.viewModel.flexSearchAddresses(null, { 'type': 'click' })

        expect(window.location.replace).toHaveBeenCalledWith('/logout')
      })

      it('Redirects user to /error on recieving a non 403 response from the AJAX call', function () {
        var deferred = $.Deferred()
        deferred.reject({
          'status': 500
        })

        spyOn($, 'getJSON').and.returnValue(deferred.promise())
        spyOn(window.location, 'replace')

        addLocation.viewModel.flexSearchAddresses(null, { 'type': 'click' })

        expect(window.location.replace).toHaveBeenCalledWith('/error')
      })
    })
  })

  it('I select address, map zooms', function () {
    var testAddress = new addLocation.Address({
      'address_type': 'property',
      'geometry': {
        'coordinates': [ 1, 1 ],
        'type': 'Point'
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

    spyOn(addLocation, 'zoomToLocation')
    spyOn(addLocation.viewModel, 'selectedAddress')
    spyOn(addLocation.addressMarker, 'markAddressLocation')

    addLocation.viewModel.flexSelectAddress(testAddress)

    expect(addLocation.addressMarker.markAddressLocation).toHaveBeenCalledWith(testAddress.geometry)
    expect(addLocation.viewModel.selectedAddress).toHaveBeenCalledWith(testAddress)
  })
})
