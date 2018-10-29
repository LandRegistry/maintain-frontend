/* global describe, it, spyOn, expect, $, address_finder, setFixtures */
describe('main.js', function () {
  describe('getAddresses', function () {
    describe('Validation errors', function () {
      it('Validation error created', function () {
        setFixtures('<div id="page-errors"></div><div id="postcode_search"></div>')

        var deferred = $.Deferred()
        deferred.resolve({
          'status': 'error',
          'search_postcode_message': 'Invalid postcode, please try again',
          'search_message_inline_message': 'Invalid postcode, please try again'
        })

        spyOn($, 'ajax').and.returnValue(deferred.promise())

        address_finder.getAddresses()

        expect($('#error-summary-list li').length).toBe(1)
        expect($('#error-message-search')).toExist()
      })

      it('Validation error appended', function () {
        setFixtures('<div id="page-errors">' +
              '<div id="error-summary">' +
              '<ul id="error-summary-list">' +
              '<li><a href="#name">Bad name</a></li>' +
              '</ul></div></div>' +
              '<div id="postcode_search"></div>')

        var deferred = $.Deferred()
        deferred.resolve({
          'status': 'error',
          'search_postcode_message': 'Invalid postcode, please try again',
          'search_message_inline_message': 'Invalid postcode, please try again'
        })

        spyOn($, 'ajax').and.returnValue(deferred.promise())

        address_finder.getAddresses()

        expect($('#error-summary-list li').length).toBe(2)
        expect($('#error-message-search')).toExist()
      })
      it('Validation error box removed', function () {
        setFixtures('<div id="page-errors">' +
                '<div id="error-summary">' +
                '<ul id="error-summary-list">' +
                '<li><a href="#street">Bad street</a></li>' +
                '<li><a href="#town">Bad town</a></li>' +
                '<li><a href="#postcode">Bad postcode</a></li>' +
                '</ul></div></div>' +
                '<div id="postcode_search"></div>')

        var deferred = $.Deferred()
        deferred.resolve({
          'status': 'success',
          'addresses': [{'address': 'abc'}]
        })

        spyOn($, 'ajax').and.returnValue(deferred.promise())

        expect($('#error-summary')).toExist()
        expect($('#error-summary-list li').length).toBe(3)

        address_finder.getAddresses()

        expect($('#error-message-search')).not.toExist()
        expect($('#error-summary')).not.toExist()
      })
      it('Only address finder validation errors removed', function () {
        setFixtures('<div id="page-errors">' +
                '<div id="error-summary">' +
                '<ul id="error-summary-list">' +
                '<li><a href="#name">Bad name</a></li>' +
                '<li><a href="#street">Bad street</a></li>' +
                '<li><a href="#town">Bad town</a></li>' +
                '<li><a href="#postcode">Bad postcode</a></li>' +
                '<li><a href="#postcode_search">Bad postcode_search</a></li>' +
                '</ul></div></div>' +
                '<div id="postcode_search"></div>')

        var deferred = $.Deferred()
        deferred.resolve({
          'status': 'success',
          'addresses': [{'address': 'abc'}]
        })

        spyOn($, 'ajax').and.returnValue(deferred.promise())

        expect($('#error-summary-list li').length).toBe(5)

        address_finder.getAddresses()

        expect($('#error-summary-list li').length).toBe(1)
        expect($('#error-message-search')).not.toExist()
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

        address_finder.getAddresses()

        expect(window.location.replace).toHaveBeenCalledWith('/logout')
      })

      it('Redirects user to /error on recieving a non 403 response from the AJAX call', function () {
        var deferred = $.Deferred()
        deferred.reject({
          'status': 500
        })

        spyOn($, 'ajax').and.returnValue(deferred.promise())
        spyOn(window.location, 'replace')

        address_finder.getAddresses()

        expect(window.location.replace).toHaveBeenCalledWith('/error')
      })
    })
  })
})
