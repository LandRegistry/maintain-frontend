/* global describe, it, spyOn, expect, $, MAP_HELPERS, addLocation, ko, beforeEach */
describe('Statutory provision autocomplete', function () {
    beforeEach(function () {
        var attributionDiv = '<input id="legislation" name="legislation" type="text"> <select id="legislation-nojs" name="legislation-nojs"> </select>'
        document.body.insertAdjacentHTML('beforebegin', attributionDiv)
        $SCRIPT_ROOT = ''

        document.addEventListener('keydown', function(e){
            keyPressed = e.keyCode;
        });

    })

    describe('script_enabled', function () {
        it('No JS select box removed when script enabled called', function () {
            spyOn($.fn, 'remove')
            statutory_provisions.script_enabled()
            expect($.fn.remove).toHaveBeenCalled()
        })
    })

    describe('Init', function () {
        it('Successfully load lists', function () {
            spyOn($.fn, 'on')
            statutory_provisions.init(["abc", "def"])
            expect($('#legislation').length).toBeGreaterThan(0)
            expect($.fn.on).toHaveBeenCalled()
        })

        it('input & replaced with and', function () {

          statutory_provisions.init(["abc and", "def"])
          expect($('#legislation').length).toBeGreaterThan(0);
          $("#legislation").val('abc &')
          $("#legislation").trigger("autocompletechange",[$( "input#legislation" )])
          expect($("#legislation").val()).toEqual('abc and')

        })
      })
})