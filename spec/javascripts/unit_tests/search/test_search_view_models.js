/* global describe, it, search, spyOn, expect, jasmine, $, ko, beforeEach, chargeLayer, MAP_HELPERS, setFixtures */
describe('Search page', function () {
  beforeEach(function () {
    ko.cleanNode($('body')[ 0 ])
    search.searchViewModel = new search.SearchViewModel()
  })

  describe('chargesInArea', function () {
    describe('Successful calls', function () {
      it('I search for postcode successful and address list is returned', function () {
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
        spyOn(search.searchViewModel.addresses, 'push')

        search.searchViewModel.searchAddresses(null, { 'type': 'click' })

        expect(search.searchViewModel.addresses.push).toHaveBeenCalledTimes(1)
      })

      it('I Search for invalid postcode', function () {
        var response = {
          'status': 'error',
          'search_message': 'Invalid search, please try again'
        }

        var deferred = $.Deferred()
        deferred.resolve(response)

        spyOn($, 'getJSON').and.returnValue(deferred.promise())
        spyOn(search.searchViewModel.addresses, 'push')
        spyOn(search.searchViewModel, 'errorMessage')

        search.searchViewModel.searchAddresses(null, { 'type': 'click' })

        expect(search.searchViewModel.addresses.push).not.toHaveBeenCalled()
        expect(search.searchViewModel.errorMessage).toHaveBeenCalledWith('Invalid search, please try again')
      })
    })

    describe('Failed calls', function () {
      it('Redirects to /logout on recieving a 403 response from the AJAX call', function () {
        var deferred = $.Deferred()
        deferred.reject({
          'status': 403
        })

        spyOn($, 'ajax').and.returnValue(deferred.promise())
        spyOn(window.location, 'replace')

        search.searchViewModel.searchAddresses(null, { 'type': 'click' })

        expect(window.location.replace).toHaveBeenCalledWith('/logout')
      })

      it('Redirects user to /error on recieving a non 403 response from the AJAX call', function () {
        var deferred = $.Deferred()
        deferred.reject({
          'status': 500
        })

        spyOn($, 'ajax').and.returnValue(deferred.promise())
        spyOn(window.location, 'replace')

        search.searchViewModel.searchAddresses(null, { 'type': 'click' })

        expect(window.location.replace).toHaveBeenCalledWith('/error')
      })
    })
  })

  it('I select address, map zooms', function () {
    var testAddress = new search.Address({
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

    spyOn(search, 'zoomToLocation')
    spyOn(search.searchViewModel, 'selectedAddress')
    spyOn(search.addressMarker, 'markAddressLocation')

    search.searchViewModel.selectAddress(testAddress)

    expect(search.zoomToLocation).toHaveBeenCalledWith([testAddress[ 'geometry' ][ 'coordinates' ]])
    expect(search.addressMarker.markAddressLocation).toHaveBeenCalledWith(testAddress.geometry)
    expect(search.searchViewModel.selectedAddress).toHaveBeenCalledWith(testAddress[ 'address' ])
  })

  describe('chargesInArea', function () {
    describe('Successful calls', function () {
      it('I search an area containing charges', function () {
        var response = {
          'status': 200,
          'data': [ {
            'cancelled': false,
            'display_id': 'LLC-FCDQF',
            'geometry': { features: [], type: 'FeatureCollection' },
            'id': 12345701,
            'type': 'Environment',
            'item': {
              'charge-creation-date': '2014-07-20',
              'charge-geographic-description': 'Exeter-220001',
              'charge-type': 'Environment',
              'further-information-location': 'local-land-charges@exeter.gov.uk',
              'further-information-reference': 'PLA/220023'
            }
          } ]
        }

        var deferred = $.Deferred()
        deferred.resolve(response)

        spyOn($, 'ajax').and.returnValue(deferred.promise())

        search.searchViewModel = new search.SearchViewModel()
        jasmine.createSpyObj(chargeLayer, [ 'drawChargesInCategories' ])
        spyOn(search.searchViewModel.charges, 'push')

        search.chargesInArea(jasmine.createSpyObj('geometry', [ 'getCoordinates' ]))

        expect(search.searchViewModel.charges.push).toHaveBeenCalledTimes(1)
      })

      it('I search an area without charges', function () {
        var deferred = $.Deferred()
        deferred.resolve({
          'status': 404
        })

        spyOn($, 'ajax').and.returnValue(deferred.promise())

        search.searchViewModel = new search.SearchViewModel()
        spyOn(search.searchViewModel.addresses, 'removeAll')
        spyOn(search.searchViewModel, 'noChargesFound')

        search.chargesInArea(jasmine.createSpyObj('geometry', [ 'getCoordinates' ]))

        expect(search.searchViewModel.addresses.removeAll).toHaveBeenCalled()
        expect(search.searchViewModel.noChargesFound).toHaveBeenCalled()
      })
    })

    describe('Failed calls', function () {
      it('I search an area and something goes wrong', function () {
        var deferred = $.Deferred()
        deferred.resolve({
          'status': 500
        })

        spyOn($, 'ajax').and.returnValue(deferred.promise())
        spyOn(window.location, 'replace')

        search.chargesInArea(jasmine.createSpyObj('geometry', [ 'getCoordinates' ]))

        expect(window.location.replace).toHaveBeenCalled()
      })

      it('I search an area with more than 1000 charges', function () {
        var deferred = $.Deferred()
        deferred.resolve({
          'status': 507
        })

        spyOn($, 'ajax').and.returnValue(deferred.promise())
        spyOn(search.searchViewModel, 'resetCategories')
        spyOn(search.searchViewModel, 'resetResults')
        spyOn(search.llcSource, 'clear')

        search.chargesInArea(jasmine.createSpyObj('geometry', [ 'getCoordinates' ]))

        expect(search.searchViewModel.resetResults).toHaveBeenCalled()
        expect(search.searchViewModel.resetCategories).toHaveBeenCalled()
        expect(search.llcSource.clear).toHaveBeenCalled()
        expect(search.searchViewModel.noChargesFound()).toBe(false)
        expect(search.searchViewModel.resultLimitExceeded()).toBe(true)
      })

      it('Redirects to /logout on recieving a 403 response from the AJAX call', function () {
        var deferred = $.Deferred()
        deferred.reject({
          'status': 403
        })

        spyOn($, 'ajax').and.returnValue(deferred.promise())
        spyOn(window.location, 'replace')

        search.chargesInArea(jasmine.createSpyObj('geometry', [ 'getCoordinates' ]))

        expect(window.location.replace).toHaveBeenCalledWith('/logout')
      })

      it('Redirects user to /error on recieving a non 403 response from the AJAX call', function () {
        var deferred = $.Deferred()
        deferred.reject({
          'status': 500
        })

        spyOn($, 'ajax').and.returnValue(deferred.promise())
        spyOn(window.location, 'replace')

        search.chargesInArea(jasmine.createSpyObj('geometry', [ 'getCoordinates' ]))

        expect(window.location.replace).toHaveBeenCalledWith('/error')
      })
    })
  })

  it('Select all checks all categories', function () {
    spyOn(chargeLayer, 'showFeatures')
    search.searchViewModel.selectAllFilters()

    search.searchViewModel.categories().forEach(function (category) {
      expect(category.checked()).toEqual(true)
    })

    expect(chargeLayer.showFeatures).toHaveBeenCalled()
  })

  it('Deselect all unchecks all categories', function () {
    spyOn(chargeLayer, 'hideFeatures')
    search.searchViewModel.deselectAllFilters()

    search.searchViewModel.categories().forEach(function (category) {
      expect(category.checked()).toEqual(false)
    })

    expect(chargeLayer.hideFeatures).toHaveBeenCalled()
  })

  it('Displays correct amount of charges', function () {
    var charges = [ {
      'cancelled': false,
      'display_id': 'LLC-1',
      'geometry': { features: [], type: 'FeatureCollection' },
      'item': {
        'charge-creation-date': '2014-07-20',
        'charge-geographic-description': 'Exeter-220001',
        'charge-type': 'Financial',
        'further-information-location': 'local-land-charges@exeter.gov.uk',
        'further-information-reference': 'PLA/220023'
      }
    },
      {
        'cancelled': false,
        'display_id': 'LLC-2',
        'geometry': { features: [], type: 'FeatureCollection' },
        'item': {
          'charge-creation-date': '2014-07-20',
          'charge-geographic-description': 'Exeter-220001',
          'charge-type': 'Planning',
          'further-information-location': 'local-land-charges@exeter.gov.uk',
          'further-information-reference': 'PLA/220023'
        }
      },
      {
        'cancelled': false,
        'display_id': 'LLC-3',
        'geometry': { features: [], type: 'FeatureCollection' },
        'item': {
          'charge-creation-date': '2014-07-20',
          'charge-geographic-description': 'Exeter-220001',
          'charge-type': 'Something else',
          'further-information-location': 'local-land-charges@exeter.gov.uk',
          'further-information-reference': 'PLA/220023'
        }
      },
      {
        'cancelled': false,
        'display_id': 'LLC-4',
        'geometry': { features: [], type: 'FeatureCollection' },
        'item': {
          'charge-creation-date': '2014-07-20',
          'charge-geographic-description': 'Exeter-220001',
          'charge-type': 'Random Charge',
          'further-information-location': 'local-land-charges@exeter.gov.uk',
          'further-information-reference': 'PLA/220023'
        }
      } ]

    search.searchViewModel.populateCharges(charges)

    expect(search.searchViewModel.otherCategory.categoryHeader()).toEqual('Other (2)')
    expect(search.searchViewModel.charges().length).toEqual(4)
  })

  describe('Open Close All', function () {
    beforeEach(function () {
      spyOn(MAP_HELPERS, 'init_controls').and.callFake(function () {})
      setFixtures('<button class="accordion-expand-all" aria-expanded="false" data-bind="click: openCloseAll">' +
        'Open all</button>')
      search.init([], '', '')
    })

    it('Open Close all toggles all accordions expansion', function () {
      $('.accordion-expand-all').click()

      search.searchViewModel.categories().forEach(function (category) {
        expect(category.expanded).toEqual(true)
      })

      expect($('.accordion-expand-all').text()).toEqual('Close all')

      $('.accordion-expand-all').click()

      search.searchViewModel.categories().forEach(function (category) {
        expect(category.expanded).toEqual(false)
      })

      expect($('.accordion-expand-all').text()).toEqual('Open all')
    })
  })
})
