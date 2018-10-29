/* global describe, it, beforeEach, MAP_HELPERS, MAP_CONFIG, spyOn, expect, jasmine, $  */
describe('Map helper functions', function() {
    var map;

    describe('Initialise map controls', function() {
        beforeEach(function() {
            setFixtures('<div id="parent"><div id="' + MAP_CONFIG.draw_control_id + '"></div></div>');
            setFixtures('<div class="ol-attribution ol-unselectable ol-control ol-uncollapsible">' +
            '<ul><li style="display: none;"></li></ul>' +
            '</div>');
        });

        it('Draw controls are added to the map', function() {
            var map = jasmine.createSpyObj('map', ['addControl']);
            var controls = {};

            MAP_HELPERS.init_controls(map, controls);

            expect(map.addControl).toHaveBeenCalledWith(controls);
            expect(map.addControl).toHaveBeenCalledTimes(4);
        });
    });

    describe('Remove OpenLayers attribution link', function() {
        beforeEach(function() {
            $('.ol-attribution.ol-unselectable.ol-control.ol-uncollapsible').remove();
            setFixtures('<div class="ol-attribution ol-unselectable ol-control ol-uncollapsible">' +
              '<ul><li style="display: none;"></li></ul>' +
              '</div>');
        });

        it('Removes link correctly', function() {
            expect(document.querySelectorAll('.ol-attribution.ol-unselectable.ol-control.ol-uncollapsible')
              .length).toEqual(1);
            MAP_HELPERS.remove_openlayers_attribution_link();
            expect(document.querySelectorAll('ol-attribution.ol-unselectable.ol-control.ol-uncollapsible')
              .length).toEqual(0);
        });
    });

    describe('Remove draw interaction when one or more exists', function() {
        beforeEach(function() {
            setFixtures('<button id="map-button-polygon" disabled></button>');
            map = jasmine.createSpyObj('map', {
                'getInteractions': [
                    jasmine.any(String),
                    new ol.interaction.Draw({})
                ],
                'removeInteraction': jasmine.createSpy()
            });
        });

        it('Removes draw interaction if it exists', function() {
            MAP_HELPERS.remove_interaction_if_polygon_button_disabled(map);
            expect(map.removeInteraction).toHaveBeenCalledTimes(1);
        });
    });

    describe('Do not remove any other interactions', function() {
        beforeEach(function() {
            setFixtures('<button id="map-button-polygon" disabled></button>');
            map = jasmine.createSpyObj('map', {
                'getInteractions': [
                  jasmine.any(String),
                  jasmine.any(String)
                ],
              'removeInteraction': jasmine.createSpy()
            });
        });

        it('Do not remove any other interactions', function() {
            MAP_HELPERS.remove_interaction_if_polygon_button_disabled(map);
            expect(map.removeInteraction).toHaveBeenCalledTimes(0);
        });
    });
});