/* global $ $SCRIPT_ROOT */
$(function () {
  $('#addresses-list').change(function () {
    var addressIndex = $(this).val()
    var address = addressesList[addressIndex]

    $('#address_line_1').val(address.line_1)
    $('#address_line_2').val(address.line_2)
    $('#address_line_3').val(address.line_3)
    $('#address_line_4').val(address.line_4)
    $('#address_line_5').val(address.line_5)
    $('#address_line_6').val(address.line_6)

    if (address.country !== undefined) {
        $('#country').val(address.country)
    } else {
        $('#country').val('United Kingdom')
    }

    $('#postcode').val(address.postcode)
    $('#uprn').val(address.uprn)

    address_finder.toggleVisibility('#addresses-list-container', false)
    address_finder.toggleVisibility('#address-fields', true)
  })

  $('#postcode_search').keypress(function (event) {
    if (event.keyCode === 13) {
      event.preventDefault()
      $('#postcode-search-button').click()
    }
  })
})

var addressesList

var address_finder = {
  init: function () {
    this.toggleVisibility('#address-finder', true)
    this.toggleVisibility('#manual-link', true)
    if (!$('#address-fields .error-message').html() && !($('#address_line_1').val())) {
      this.toggleVisibility('#address-fields')
    }
  },

  resetFormValuesAndErrorMessages: function () {
    $('#postcode').val('')
    $('#addresses-list').html('<option></option>')

    if ($('#error-message-search')) {
            // Only remove validation errors from address finder not all errors on page
      $('#error-summary-list li').each(function () {
        var ref = $('a', this).attr('href')
        if (ref === '#street' || ref === '#town' || ref === '#postcode' || ref === '#postcode_search') {
          $(this).remove()
        }
      })

            // Remove error box if no errors remain
      if ($('#error-summary-list li').length === 0) {
        $('#error-summary').remove()
      }

      $('#error-message-search').remove()
      $('#address-finder').removeClass('form-group-error')
      $('#street-group').removeClass('form-group-error')
      $('#street-error-message').remove()
      $('#town-group').removeClass('form-group-error')
      $('#town-error-message').remove()
      $('#postcode-group').removeClass('form-group-error')
      $('#postcode-error-message').remove()
    }
  },

  toggleVisibility: function (elementId, show) {
    if (show) {
      $(elementId).removeClass('hidden')
    } else {
      $(elementId).addClass('hidden')
    }
  },

  displayErrorMessages: function (response) {
    if ($("#inline_error_message_desc").length > 0){
        $( "#error-summary" ).remove()
        $( "#charge_geo_desc_div" ).removeClass('form-group-error')
        $("#inline_error_message_desc").remove()
    }
    if (!$('#error-summary').html()) {
      var errorMsg = '<div id="error-summary" class="error-summary" role="group" ' +
                'aria-labelledby="error-summary-heading-example-1" tabindex="-1">' +
                '<h1 class="heading-medium error-summary-heading" id="error-summary-heading-example-1">' +
                'There are errors on this page</h1>' +
                '<ul id="error-summary-list" class="error-summary-list">' +
                '<li><a href="#postcode_search">' + response.search_postcode_message + '</a></li>' +
                '</ul></div>'
      $(errorMsg).insertAfter('#page-errors')
    } else {
      $('#error-summary-list').append('<li id="error-message-search-item"><a href="#postcode_search">' + response.search_postcode_message + '</a></li>')
    }
    if (!$('#addresses-list-container').hasClass('hidden')){
        this.toggleVisibility('#addresses-list-container', false)
    }
    var inlineMsg = '<span class="error-message" id="error-message-search">' + response.search_postcode_message + '</span>'
    $('#postcode_search').before(inlineMsg)
    $('#address-finder').addClass('form-group-error')
  },

  handleAddressResponse: function (response) {
    if (response.status === 'success') {
      var addresses = response.addresses
      addressesList = addresses
      for (var i = 0; i < addresses.length; i++) {
        $('#addresses-list').append($('<option>', {
          value: i,
          text: addresses[i].address
        }))
      }
      this.toggleVisibility('#addresses-list-container', true)
    } else {
      this.displayErrorMessages(response)
    }
  },

  getAddresses: function () {
    this.toggleVisibility('#address-fields')
    this.resetFormValuesAndErrorMessages()

    $.getJSON($SCRIPT_ROOT + '/address-finder/_search', {
      search_term: $('#postcode_search').val()
    })

        .done(function (response) {
          address_finder.handleAddressResponse(response)
        })

        .fail(function (response) {
          if (response.status === 403) {
            window.location.replace('/logout')
          } else {
            window.location.replace('/error')
          }
        })
  }
}
