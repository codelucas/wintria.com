
/* REALLY IMPORTANT, HOGAN AND DJANGO'S CURLY BRACELETS INTERFERE WITH EACHOTHER.
   ANY .JS WITH HOGAN/TYPEAHEAD CODE MUST BE IN IT'S OWN .JS FILE */

$(document).ready(function() {
    $('.main_dropdown .typeahead').typeahead([{
        name: 'splash-typeahead',
        remote: root_url + '/static/autocomplete/%QUERY.json',
        prefetch: {
           url: root_url + '/static/autocomplete/prefetch.json',
           ttl: 0
        },
        template: '<span style="color:#000;font-size:28px;font-weight:200;">{{value}}</span>',
        limit: 10,
        rateLimitWait: 170,
        engine: Hogan
    }]).on('typeahead:selected', submit_query);
});


function submit_query() {
    $('#splash_input').submit();
}

function focus_input() {
     $('#query_bar').focus();
}
