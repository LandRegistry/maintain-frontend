module.exports = function (config) {
  config.set({
    basePath: '',
    frameworks: ['jasmine-jquery', 'jasmine'],
    plugins: ['karma-jasmine', 'karma-chrome-launcher', 'karma-coverage', 'karma-phantomjs-launcher', 'karma-jasmine-jquery', 'karma-spec-reporter'],
    files: [

      // External Dependencies:
      'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
      'https://openlayers.org/en/v4.0.1/build/ol.js',
      'https://cdnjs.cloudflare.com/ajax/libs/proj4js/2.3.17/proj4-src.js',
      'https://cdnjs.cloudflare.com/ajax/libs/knockout/3.4.2/knockout-min.js',
      'https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js',

      // Map Dependencies:
      'maintain_frontend/map/static/js/map_styles.js',
      'maintain_frontend/map/static/js/master_map_vector_layer.js',
      'maintain_frontend/map/static/js/snap_to_vector_layer.js',
      'maintain_frontend/map/static/js/map_undo.js',
      'maintain_frontend/map/static/js/address_marker.js',
      'maintain_frontend/map/static/js/map_controls.js',
      'maintain_frontend/map/static/js/map_helpers.js',
      'maintain_frontend/map/static/js/map_config.js',
      'spec/javascripts/setup/map_config.js',
      'maintain_frontend/map/static/js/geoserver.js',
      'spec/javascripts/setup/geoserver_config.js',
      'maintain_frontend/map/static/js/map.js',
      'maintain_frontend/map/static/js/full-screen-map-sidebar.js',

      // Add Land Charge Dependencies:
      'maintain_frontend/add_land_charge/static/js/*.js',

      // Add LON Dependencies:
      'maintain_frontend/add_lon/static/js/*.js',

      // Address Finder Dependencies:
      'maintain_frontend/address_finder/static/js/main.js',

      // Search Dependencies:
      'maintain_frontend/search/static/js/map_styles.js',
      'maintain_frontend/search/static/js/charge_layer.js',
      'maintain_frontend/search/static/js/feature_helpers.js',
      'maintain_frontend/search/static/js/search_view_models.js',
      'maintain_frontend/search/static/js/search.js',
      'maintain_frontend/search/static/js/map_events.js',

      // Unit Tests:
      'spec/javascripts/unit_tests/add_land_charge/*.js',
      'spec/javascripts/unit_tests/add_lon/*.js',
      'spec/javascripts/unit_tests/address_finder/*.js',
      'spec/javascripts/unit_tests/map/*.js',
      'spec/javascripts/unit_tests/search/*.js',
      'spec/javascripts/unit_tests/undo/*.js'

    ],
    exclude: [],
    preprocessors: {
      'maintain_frontend/map/static/js/*.js': 'coverage',
      'maintain_frontend/add_land_charge/static/js/*.js': 'coverage'
    },
    reporters: ['spec', 'coverage'],
    port: 9876,
    colors: true,
    logLevel: config.LOG_INFO,
    autoWatch: false,
    browsers: ['PhantomJS'],
    singleRun: false,
    concurrency: Infinity
  })
}
