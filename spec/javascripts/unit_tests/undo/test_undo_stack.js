
describe("Save Geometries javascript tests", function () {
    beforeEach(function() {
        var fixture = '<button id="map-button-undo">';
        document.body.insertAdjacentHTML('beforebegin', fixture);
    });

    it("enables the undo button when the undo stack has items", function () {
        spyOn(MAP_UNDO, 'get_geometries').and.callFake(function() {
            return {
                "type":"FeatureCollection",
                "features":[ {
                    "type":"Feature",
                    "geometry": {
                            "type":"Polygon",
                            "coordinates":[[[511076,381319],[502935,344754],[460299,365124],[478395,392099],[511076,381319]]]
                        },
                    "properties":{
                        "id":1
                    }
                } ] };
        });
        MAP_UNDO.store_state();

        expect(MAP_UNDO.undo_stack.length).toBe(1);
        var button = document.getElementById('map-button-undo');
        expect(button.disabled).toBe(false);
    });

    it("disables the undo button when the undo stack has no items", function () {
        MAP_UNDO.clear_undo_stack();
        expect(MAP_UNDO.undo_stack.length).toBe(0);
        var button = document.getElementById('map-button-undo');
        expect(button.disabled).toBe(true);

    });

    it("limits the undo stack to 10 items", function () {
        spyOn(MAP_UNDO, 'get_geometries').and.callFake(function() {
            return {
                "type":"FeatureCollection",
                "features":[ {
                    "type":"Feature",
                    "geometry": {
                            "type":"Polygon",
                            "coordinates":[[[511076,381319],[502935,344754],[460299,365124],[478395,392099],[511076,381319]]]
                        },
                    "properties":{
                        "id":1
                    }
                } ] };
        });

        for(var i=0; i<20; i++) {
            MAP_UNDO.store_state();
        }
        expect(MAP_UNDO.undo_stack.length).toBe(10);
    });

    it("calls openlayers removeLastPoint while drawing", function() {
        MAP_CONTROLS.current_interaction = new ol.interaction.Draw({
            features: MAP_CONFIG.draw_features,
            type: 'LineString',
            style: draw_layer_styles.style[draw_layer_styles.DRAW]
        });

        spyOn(MAP_UNDO, 'openlayers_undo')
        spyOn(MAP_UNDO, 'remove_undo')
        MAP_UNDO.undo();
        expect(MAP_UNDO.openlayers_undo).toHaveBeenCalled();
        expect(MAP_UNDO.remove_undo).not.toHaveBeenCalled();
    });

    it("calls llc undo when not drawing", function() {
        MAP_CONTROLS.current_interaction = null;

        spyOn(MAP_UNDO, 'openlayers_undo')
        spyOn(MAP_UNDO, 'remove_undo')
        MAP_UNDO.undo();
        expect(MAP_UNDO.openlayers_undo).not.toHaveBeenCalled();
        expect(MAP_UNDO.remove_undo).toHaveBeenCalled();
    });

    it("disables the undo button on demand", function() {
        MAP_UNDO.enable_undo_button(false);
        var button = document.getElementById('map-button-undo');
        expect(button.disabled).toBe(true);
    });

    it("enables the undo button on demand", function() {
        MAP_UNDO.enable_undo_button(true);
        var button = document.getElementById('map-button-undo');
        expect(button.disabled).toBe(false);
    });

    it("can store and retrieve geometries", function() {
        var geo_in = {
            "type":"FeatureCollection",
            "features":[ {
                "type":"Feature",
                "geometry": {
                        "type":"Polygon",
                        "coordinates":[[[511076,381319],[502935,344754],[460299,365124],[478395,392099],[511076,381319]]]
                    },
                "properties":{
                    "id":1
                }
            } ] };

        var deferred = $.Deferred()
        deferred.resolve({
          'status': 200,
          'data': []
        })

        spyOn($, 'ajax').and.returnValue(deferred.promise())

        MAP_CONFIG.draw_source.clear();
        MAP_UNDO.put_geometries(geo_in);
        expect(MAP_CONFIG.draw_source.getFeatures().length).toBe(1);

        geo_out = JSON.parse(MAP_UNDO.get_geometries());
        expect(geo_out['type']).toBe('FeatureCollection');
        expect(geo_out['features'][0]['geometry']['coordinates'][0][0][0]).toBe(511076);
    });
});
