
describe("Save Geometries javascript tests", function () {
    beforeEach(function() {
        var fixture = '<button id="map-button-edit"></button><button id="map-button-remove"></button><button id="map-button-remove-all"></button>';
        document.body.insertAdjacentHTML('beforebegin', fixture);
    });

    it("load previous data", function () {
        input = '{&#39;type&#39;:&#39;FeatureCollection&#39;,' +
            '&#39;features&#39;:[' +
            '{&#39;type&#39;:&#39;Feature&#39;,' +
            '&#39;geometry&#39;:{' +
            '&#39;type&#39;:&#39;Polygon&#39;,' +
            '&#39;coordinates&#39;:[' +
            '[[511076.08598934463,381319.1389185938],' +
            '[502935.0162093069,344754.81621829123],' +
            '[460299.51643357374,365124.6766137525],' +
            '[478395.29646112275,392099.3797708411],' +
            '[511076.08598934463,381319.1389185938]]]},' +
            '&#39;properties&#39;:{&#39;id&#39;:1}}]}';

        var deferred = $.Deferred()
        deferred.resolve({
            'status': 200,
            'data': []
        })

        spyOn($, 'ajax').and.returnValue(deferred.promise())

        MAP_CONFIG.draw_source.clear();

        expect(MAP_CONFIG.draw_source.getFeatures().length).toBe(0);

        load_previous_data(input);

        expect(MAP_CONFIG.draw_source.getFeatures().length).toBe(1);
    });

    it("load no previous data if null", function () {

        MAP_CONFIG.draw_source.clear();

        expect(MAP_CONFIG.draw_source.getFeatures().length).toBe(0);

        load_previous_data(null);

        expect(MAP_CONFIG.draw_source.getFeatures().length).toBe(0);

    });

    it("load no previous data if empty", function () {

        MAP_CONFIG.draw_source.clear();

        expect(MAP_CONFIG.draw_source.getFeatures().length).toBe(0);

        load_previous_data('');

        expect(MAP_CONFIG.draw_source.getFeatures().length).toBe(0);

    });

    it("load no previous data if json invalid", function () {

        MAP_CONFIG.draw_source.clear();

        expect(MAP_CONFIG.draw_source.getFeatures().length).toBe(0);

        load_previous_data('{"abc" = "123"}');

        expect(MAP_CONFIG.draw_source.getFeatures().length).toBe(0);

    });
});
