var statutory_provisions = {
    init : function (entry_list) {
        $( "input#legislation" ).autocomplete({
            minLength: 1,
            source: function(request, response) {
                var term = request.term.replace(new RegExp(' &', 'gi'), " and").replace(new RegExp('&', 'gi'), " and");
                var matcher = new RegExp($.ui.autocomplete.escapeRegex(term), "i");
                response($.map(entry_list, function (e) {
                        if (matcher.test(e.replace(new RegExp('&', 'gi'), "and"))) {
                            return e;
                        }
                    }
                ))
            },
            dataType: "json",
        });
        $( "input#legislation" ).on( "autocompletechange", function( e, ui ) {
            if(!ui.item){
                var input = e.target.value.replace(new RegExp('&', 'gi'), "and");
                //check against all values in case of strangeness on loading page with pre-populated value or keyboard input
                for (var i = 0; i < entry_list.length; i++) {
                    if(entry_list[i].toLowerCase() === input.toLowerCase()){
                        ui.item = entry_list[i];
                        //put value into input to stop pure keyboard users submitting weird text casing
                        $( "input#legislation" ).val(entry_list[i]);
                    }
                }
                if(!ui.item){
                    e.target.value = "";
                    e.target.focus();
                }
            }
        });
    },

    script_enabled: function(){
        if ($("#legislation-nojs")) {
            $("#legislation-nojs").remove();
        }
    }
};

//Fire autocompletechange on submit in case user hits enter from text box
$( '#statutory-provision-form' ).submit(function() {
    $( "input#legislation" ).trigger("autocompletechange", [$( "input#legislation" )]);
});
