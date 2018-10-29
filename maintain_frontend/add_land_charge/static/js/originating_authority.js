var authoritySearch = {
    init: function (authorities) {
        $( "input#authority-search-field" ).autocomplete({
            minLength: 1,
            delay: 0,
            source: authorities,
            dataType: "json"
        });
    }
};
