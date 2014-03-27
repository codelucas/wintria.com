/**
 * Created with PyCharm.
 * User: louyang
 * Date: 8/9/13
 * Time: 10:39 AM
 * To change this template use File | Settings | File Templates.
 */



$(document).ready(function() {
  $('.main_dropdown .typeahead').typeahead([{
     name: 'main-query-typeahead',
     remote: root_url + '/static/autocomplete/%QUERY.json',
     prefetch: {
        url: root_url + '/static/autocomplete/prefetch.json',
        ttl: 0
     },
     template: '<span style="color:#000;font-size:20px;font-weight:200;">{{value}}</span>',
     limit: 10,
     rateLimitWait: 170,
     engine: Hogan
  }]).on('typeahead:selected', submit_query);

});


function submit_query() {
   $('#main_query_input').submit();
}