var is_lr = false
var organisation = "Test City Council"
var geoserver_url = "test_url"
var geoserver_token = "test_token"
var params = {
    'LAYERS': 'llc:boundaries_organisation_combined',
    'VERSION': '1.1.1',
    'FORMAT': 'image/png',
    'TILED': true
};

describe("Configure geoserver layer for user", function () {
  it("calls geoserver with the correct values", function () {
    params['STYLES'] = 'authority_boundary_maintain';
    params['ENV'] = 'la_name:' + organisation.replace("&#39;","\'");

    configure_geoserver_layer_for_user(is_lr, organisation, geoserver_url, geoserver_token)

    // The following object property names are from the minified openlayers library we are using at time of writing
    expect(GEOSERVER_CONFIG.boundaries_layer.I.source.S).toEqual(geoserver_url + "/geoserver/llc/" + geoserver_token + "/wms?")
    expect(GEOSERVER_CONFIG.boundaries_layer.I.source.i.ENV).toEqual("la_name:" + organisation)
    expect(GEOSERVER_CONFIG.boundaries_layer.I.source.i.STYLES).toEqual("authority_boundary_maintain")

  })
})
