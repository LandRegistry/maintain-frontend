/* global $ */
var sidebar = sidebar || {};

/** Defines functionality for the map's sidebar. */
(function (sidebar) {
  var SIDEBAR = '#full-screen-map-sidebar'
  var EXPAND_CLOSE_BUTTON = '#expand-close-button'
  var EXPAND_CLOSE_BUTTON_IMAGE = '#expand-close-button img'

  var STATIC_CONTENT_URL = '#static_content_url'
  var ARROW_COLLAPSE_IMAGE_URL = '/images/arrow_collapse.png'
  var ARROW_OPEN_IMAGE_URL = '/images/arrow_open.png'

  /**
   * Initialises the sidebar namespace. Should be called prior to use.
   * @public
   */
  sidebar.initialise = function () {
    registerEvents()
  }

  /**
   * Expand the map's sidebar.
   * @public
   */
  sidebar.expandSidebar = function () {
    $(SIDEBAR).animate({
      'margin-left': '0'
    }, 100)
    $(EXPAND_CLOSE_BUTTON).removeClass('open')
    $(EXPAND_CLOSE_BUTTON).addClass('close')
    $(EXPAND_CLOSE_BUTTON_IMAGE).attr('src', $(STATIC_CONTENT_URL).val() + ARROW_COLLAPSE_IMAGE_URL)
  }

  /**
   * Collapse the map's sidebar.
   * @public
   */
  sidebar.collapseSidebar = function () {
    $(SIDEBAR).animate({
      'margin-left': '-1000px'
    }, 100)
    $(EXPAND_CLOSE_BUTTON).removeClass('close')
    $(EXPAND_CLOSE_BUTTON).addClass('open')
    $(EXPAND_CLOSE_BUTTON_IMAGE).attr('src', $(STATIC_CONTENT_URL).val() + ARROW_OPEN_IMAGE_URL)
  }

  /**
   * Registers all sidebar events.
   * @private
   */
  function registerEvents () {
    /**
     * Onclick event that expands and collapses the sidebar.
     */
    $(EXPAND_CLOSE_BUTTON).click(function () {
      if ($(this).hasClass('close')) {
        sidebar.collapseSidebar()
      } else {
        sidebar.expandSidebar()
      }
    })
  }
})(sidebar)
