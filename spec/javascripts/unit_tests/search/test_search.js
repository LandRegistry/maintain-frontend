/* global describe, it, spyOn, expect, $, search */
describe('search.js', function () {
  describe('chargesInArea', function () {
    describe('Failed calls', function () {
      const GEOMETRY = {
        getCoordinates: function () {}
      }

      it('Redirects to /logout on recieving a 403 response from the AJAX call', function () {
        var deferred = $.Deferred()
        deferred.reject({
          'status': 403
        })

        spyOn($, 'ajax').and.returnValue(deferred.promise())
        spyOn(window.location, 'replace')

        search.chargesInArea(GEOMETRY)

        expect(window.location.replace).toHaveBeenCalledWith('/logout')
      })

      it('Redirects user to /error on recieving a non 403 response from the AJAX call', function () {
        var deferred = $.Deferred()
        deferred.reject({
          'status': 500
        })

        spyOn($, 'ajax').and.returnValue(deferred.promise())
        spyOn(window.location, 'replace')

        search.chargesInArea(GEOMETRY)

        expect(window.location.replace).toHaveBeenCalledWith('/error')
      })
    })
  })
})
