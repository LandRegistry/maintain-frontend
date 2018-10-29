/* global $, ol, map, $SCRIPT_ROOT, MAP_HELPERS, MAP_CONTROLS */
var addLonLocation = {
  init: function () {
    $('#search').bind('click', addLonLocation.performSearch);
    $('#search_term').keyup(function (event) {
      if (event.keyCode === 13) {
        $('#search').click()
      }
    });

    // LON Map Controls
    var controls = new MAP_CONTROLS.Controls([
        MAP_CONTROLS.polygon_button(),
        MAP_CONTROLS.point_button(),
        MAP_CONTROLS.line_button(),
        MAP_CONTROLS.edit_button(),
        MAP_CONTROLS.copy_button(),
        MAP_CONTROLS.remove_button(),
        MAP_CONTROLS.remove_all_button(),
        MAP_CONTROLS.undo_button(),
        MAP_CONTROLS.snap_to()
    ]);

    MAP_HELPERS.init_controls(map, controls);
  },

  performSearch: function () {
    $.getJSON($SCRIPT_ROOT + '/_search/text/v1', {
      search_term: $('#search_term').val()
    })

    .done(function(response) {
      addLonLocation.processResponse(response)
    })

    .fail(function(response) {
      if (response.status === 403) {
        window.location.replace('/logout')
      } else {
        window.location.replace('/error')
      }
    })
  },

  processResponse: function (response) {
    if (response.status === 'success') {
            // Remove the whole error summary if search is the only error
      if ($('#search-error-list-item').length && $('#error-summary-list li').length === 1) {
        $('#error-summary').remove()
      }

      $('#error-message-search').remove()
      $('#search-error-list-item').remove()
      $('#search-fieldset').removeClass('form-group-error')

      var extent = new ol.extent.boundingExtent(response.coordinates)
      map.getView().fit(extent, {duration: 1000})
    } else {
      var inlineMsg = '<span class="error-message" id="error-message-search">' +
                            response.search_message + '</span>'

      if ($('#error-summary').length) {
        if ($('#error-summary-list:contains(' + response.search_message + ')').length === 0) {
          $('#error-summary-list').append('<li id="search-error-list-item"><a href="#search_term">' +
                response.search_message + '</a></li>')
          $('#search_term').before(inlineMsg)
        }
      } else {
        var errorMsg = '<div id="error-summary" class="error-summary" role="group" ' +
                    'aria-labelledby="error-summary-heading-example-1" tabindex="-1">' +
                    '<h2 class="heading-medium error-summary-heading" id="error-summary-heading-example-1">' +
                    'There are errors on this page</h2>' +
                    '<ul id="error-summary-list" class="error-summary-list">' +
                    '<li id="search-error-list-item"><a href="#search_term">' + response.search_message + '</a></li>' +
                    '</ul></div>'

        $('#search-error').html(errorMsg)
        $('#search_term').before(inlineMsg)
        $('#search-fieldset').addClass('form-group-error')
      }
    }
  }
}