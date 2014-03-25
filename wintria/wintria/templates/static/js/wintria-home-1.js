/* IMPORTANT: The variables "news" and "source_count" are loaded in the template
            which calls this .js file, they must be in the django html template
            due to dynamic rendering reasons.
            var news = { cur_articles|jsonify };
            var source_count = { cur_sources|length }; */

  var DEFAULT_INTERVAL = 1500; // 1000 = 1 second, default = 2500
  var PAUSED_INTERVAL = 10000000;
  var PLAY_DELAY = 4000;
  var START_INTERVAL = 0;
  var reload_interval = START_INTERVAL;
  var hit_last_tile = false;
  //var saved_interval = START_INTERVAL;
  var well_num = 1;
  var refreshIntervalId = null;
  var TILE_COUNT = 12;
  var MAX_KEYS = 10;
  var news_index = 0;

  // Twitter popup vars
  var popup_width = 873;
  var popup_height = 926;
  var popup_left = (screen.width/2)-(popup_width/2);
  var popup_top = (screen.height/2)-(popup_height/2);

  var saved_dynamic = false;
  var saved_stream_list = false;
  var is_static = false;

  var stream_pause_html = "" +
      "<div class='alert alert-error' style='background-color:transparent;padding:0;border:0;padding-top:25px;padding-bottom:7px;text-align:center;'>" +
         "<i class='icon-pause icon-3' style='color:#e74c3c;font-size:40px;margin-top:-5px;'></i>" +
             "<span style='font-size:28px;margin-left:30px;color:#e74c3c;font-weight:200;'>" +
         "<i>tap anywhere on the screen to unpause</i>. tap again to pause.</span>" +
      "</div>";

    /*  +	Indicates a space (spaces cannot be used in a URL).	%2B
        /	Separates directories and subdirectories.	%2F
        ?	Separates the actual URL and the parameters.	%3F
        %	Specifies special characters.	%25
        #	Indicates bookmarks.	%23
        &	Separator between parameters specified in the URL.	%26
    */
    /*
      function url_domain(data) {
          var a = document.createElement('a');
          a.href = data;
          return a.hostname;
      }
    */
  function urlify_title(title) {
      return title.substring(0, 75).
          replace(/ /g, "_").replace('%', '_').replace('?', '_').
          replace('/', '_').replace('#', '_').replace('&', '_')
  }

  function submit_query() {
     $('#main_query_input').submit();
  }

  function replay() {
     well_num = 1;
     hit_last_tile = false;
     if (!is_static) {
         var pause_area_JQ = $(".the-pause-area");
         pause_area_JQ.html(saved_dynamic);
     }
     reload_interval = START_INTERVAL;
     $(".well-large").removeClass("articles-background-grayed-out");
     $(".article").css("border", "1px solid #E3E3E3");
     window.clearInterval(refreshIntervalId);
     refreshIntervalId = window.setInterval(reload_article, reload_interval);
  }

  function start() {
     well_num = 1;
     hit_last_tile = false;
     reload_interval = START_INTERVAL;
     $(".well-large").removeClass("articles-background-grayed-out");
     $(".article").css("border", "1px solid #E3E3E3");
     window.clearInterval(refreshIntervalId);
     refreshIntervalId = window.setInterval(reload_article, reload_interval);
  }

  function pause(human_paused) {
     if (reload_interval == PAUSED_INTERVAL){
         return;
     }
     // param necessary b/c we force pause it when there are few
     // results and we not on grid system saved_interval = reload_interval;
     if (human_paused) {
         $(".well-large").addClass("articles-background-grayed-out");
         $(".article").css("border", "0px solid #E3E3E3");
         var streams = $(".selected-streams-list");
         saved_stream_list = streams.html();
         streams.html(stream_pause_html);
     }
     reload_interval = PAUSED_INTERVAL;
     window.clearInterval(refreshIntervalId);
     refreshIntervalId = window.setInterval(reload_article, reload_interval);
  }

  function restore() {
     reload_interval = DEFAULT_INTERVAL;
     window.clearInterval(refreshIntervalId);
     refreshIntervalId = window.setInterval(reload_article, reload_interval);
  }

  function play(initial_query) {

     if (!initial_query && saved_stream_list != false) {
        var streams = $(".selected-streams-list"); // HOW THE HELL DID I FIX THIS
        streams.html(saved_stream_list);
        saved_stream_list = false;
     }

     $(".well-large").removeClass("articles-background-grayed-out");
     $(".article").css("border", "1px solid #E3E3E3");

     if (initial_query) {
        reload_interval = PAUSED_INTERVAL;
        window.clearInterval(refreshIntervalId);
        refreshIntervalId = window.setInterval(reload_article, reload_interval);
        setTimeout(restore, PLAY_DELAY);
     }
     else {
         restore();
     }
  }

  function toggle_speed() {
      if (is_static) return;
      if (reload_interval == PAUSED_INTERVAL) { play(false); }
      else { pause(true); }
  }

  function query_main() {
     $.post('/api/query_main/', { query:$("#appendedInputButton-02").val() },
         function(response) {
             news = $.parseJSON(response.updated_news);
             source_obj = $.parseJSON(response.source_json);
             related_keys = response.related_keys;
             source_vals = [];
             for (var i = 0; i < source_obj.length; i++) {
                 source_vals.push(source_obj[i]["id"]);
             }
             var stream_list_JQ = $(".sources-list");
             stream_list_JQ.empty();
             for (var j = 0; j < source_vals.length; j++) {
                  var domain_id = source_vals[j].split("&del")[0];
                  var description = source_vals[j].split("&del")[1];
                  var logo_url = source_vals[j].split("&del")[2];

                  stream_list_JQ.append(
                      format_stream_list(logo_url, domain_id, description)
                  );
             }
             var key_list = $(".keyword-list");
             key_list.empty();
             for (var m=0; m<related_keys.length; m++) {
                 key_list.append(format_key_list(related_keys[m]));
             }
             // Wait for the callback before doing anything.
             if (reload_interval == PAUSED_INTERVAL) { start(); }
             else { replay(); }
         }, 'json'
     );
   }

  function to_keyword_string(keywords) {
      var base = "";
      var twitter_url = "https://twitter.com/search?q=%23";
      for (var i=0; i<keywords.length; i++) {
         base += '<a href=' + '"'+twitter_url+keywords[i]+'"' +
             'class="well_tag twitter_popup">';
         base += '#' + keywords[i] + '</a>' + ' ' ;
      }
      return base;
  }

  function display_undef() {
      var pause_area_JQ = $(".the-pause-area");
      var articles_string = '<div class="row-fluid">';
      articles_string += '<img src="'+root_url+'/static/images/no_results.png" />';
      articles_string += '</div>';
      pause_area_JQ.html(articles_string);
  }


  function display_static(news) {
      var pause_area_JQ = $(".the-pause-area");
      var articles_string = '<div class="row-fluid">';
      for (var i=0; i<news.length; i++) {
          var article = news[i].fields;
          var inc_digit = news[i].pk;
          var title = article.title;
          //var indiv_url = article.url;
          var full_url = root_url + "/" + inc_digit + "/" + urlify_title(article.title);
          //var fallback_url = root_url + "/static/images/main_sq_logo.png";
          var keywords = article.keywords.split("@@").slice(0, MAX_KEYS + 20);
          var keyword_string = to_keyword_string(keywords);
          var thumb_url = article.thumb_url;

          articles_string +=
          '<div class="article span10" style="margin-left:100px;height:57px;margin-bottom:5px;">' +
              '<div style="height:30px;overflow:hidden;">' +
                  '<a href=' + full_url + ' id=' + inc_digit + ' target="_blank" class="span12 article_link">' +
                      '<div style="margin-bottom:8px;"><span style="font-size:22px;font-color:#317EAC;">'
                            + title + '</span></div>' +
                   '</a>' +
              '</div>' +
              //'<div class="well_image" name="none" style="height:40px;background-image:url('+ thumb_url +')">' +
                  '<div class="tiled-keywords row-fluid" style="display:none;word-break:break-word;">'
                        + keyword_string + '</div>' +
             // '</div>' +
          '</div>';
      }

      if (news.length == 0) {
          articles_string += '<img src="'+root_url+'/static/images/no_results.png" />';
      }
      articles_string += '</div>';
      pause_area_JQ.html(articles_string);
  }

  function reload_article() {
    if (!saved_dynamic) { // Just do this once per load.
        var pause_area_JQ = $(".the-pause-area");
        saved_dynamic = pause_area_JQ.html(); // Save this for later
    }

    // TODO, sometimes we have an unusual error where var news DOES NOT EXIST
    //if(typeof news === 'undefined' || news == null) {
    //    pause(false);
    //    display_undef();
    //    return;
    //}
    if (news.length <= 20) {
        is_static = true;
        pause(false);
        display_static(news);
        return;
    }
    else if (news.length > 20 && is_static) { // was static
        var pause_area_JQ = $(".the-pause-area");
        pause_area_JQ.html(saved_dynamic);
        is_static = false;
    }
    //alert(news_index+" " + news.length);
    try {
        var article = news[news_index].fields;
    }
    catch(err) {
        pause(false);
        display_undef();
        return;
    }
    var inc_digit = news[news_index].pk;

    news_index += 1;
    if (news_index == news.length) { news_index = 0; }

    var title = article.title;
    var extend_well = "false"; // must be string format, were shoving it in css
    if (article.title.length > 65) {
        extend_well = "true";
    }
    //var indiv_url = article.url;
    var full_url = root_url + "/" + inc_digit + "/" + urlify_title(article.title);
    //var domain = url_domain(indiv_url);
    //var fallback_url = root_url + "/static/images/main_sq_logo.png";
    //var age = article.timestamp;  // CONVERT THIS INTO ACTUAL AGE LATER!!!
    var keywords = article.keywords.split("@@").slice(0, MAX_KEYS + 1);
    var keyword_string = to_keyword_string(keywords);
    var thumb_url = article.thumb_url;


    var cur_well = $('.well.well-large.' + well_num);
    if (cur_well.hasClass("loading-article")) {
        cur_well.removeClass("loading-article");
    }

    if (cur_well.hasClass("mouse-inside-article")) {
        if (well_num == TILE_COUNT) {
            well_num = 1;
            if (!hit_last_tile) {
                play(true);
                hit_last_tile = true;
            }
        }
        else {
            well_num += 1;
        }
    }

    // DO NOT cache this selector, we are altering well_num.
    $('.well.well-large.' + well_num).html(
        '<div class="row-fluid" style="height:100%;">' +
            '<div class="top_half" name="'+ extend_well + '" style="height:30%;overflow:hidden;">' +
                '<a href=' + full_url + ' id=' + inc_digit + ' target="_blank" class="span12 article_link">' +
                    '<div style="margin-bottom:8px;"><span style="font-size:22px;font-color:#317EAC;">'
                            + title + '</span></div>' +
                '</a>' +
            '</div>' +
            /*  We have a trick. name is our placeholder for our background url
                when we make it none when its hovered over */
          '<div class="well_image" name="none" style="background-image:url('+ thumb_url +')">' +
              '<div class="tiled-keywords row-fluid" style="display:none;word-break:break-word;">'
                    + keyword_string + '</div>' +
          '</div>' +
        '</div>'
      ).hide().fadeIn(500);

    if (well_num <= TILE_COUNT) {
      well_num += 1;
    }
    if (well_num > TILE_COUNT) {
        well_num = 1;
        // WARNING: IF A USER HOVERS OVER LAST TILE, IT WILL BE INFINITE FAST
        if (!hit_last_tile) {
            play(true);
            hit_last_tile = true;
        }
    }
  }


$(document).ready(function() {
  var pause_area_JQ = $(".the-pause-area");
  pause_area_JQ.on( {mouseenter: function() {
       //This line below disables article skipping when mouse is over hover in the article preload
       if (!$(this).hasClass("loading-article")) {
          $(this).addClass("mouse-inside-article");

           // if the title isn't that long, don't extend percentage
          if ($(this).find(".top_half").attr("name") == "true") {
            $(this).find(".top_half").css("height", "45%");
          }
       }
       $(this).find(".tiled-keywords").slideDown( 200 );
       var bg_img = $(this).find(".well_image").css("background-image");
       $(this).find(".well_image").attr("name", bg_img);
       $(this).find(".well_image").css("background-image", "none");
  }, mouseleave: function() {
       //This line below disables article skipping when mouse is over hover in the article preload
       if (!$(this).hasClass("loading-article")) {
          $(this).removeClass("mouse-inside-article");

          if ($(this).find(".top_half").attr("name") == "true") {
            $(this).find(".top_half").css("height", "30%");
          }
       }
       $(this).find(".tiled-keywords").slideUp( 200 );
       var bg_img = $(this).find(".well_image").attr("name");
       $(this).find(".well_image").css("background-image", bg_img);
       var bg_img = $(this).find(".well_image").attr("name", "none");
  }}, ".article");

  //This will load the articles very quickly, then set it off to a normal pace
  refreshIntervalId = window.setInterval(reload_article, reload_interval);

  $("#wrap").click(function(event) { toggle_speed(); });

  $('body').tooltip({
      selector: '[rel=tooltip]'
  });

  $(document).on('click', 'a.twitter_popup', function () {
      newwindow = window.open($(this).attr('href'),'','height='+popup_height+',width='+popup_width+
          ',top='+popup_top+',left='+popup_left);
      if (window.focus) { newwindow.focus(); }
      return false;
  });

  $('.main_dropdown .typeahead').typeahead([{
     name: 'main-query-typeahead',
     remote: root_url + '/static/autocomplete/%QUERY.json',
     prefetch: {
        url: root_url + '/static/autocomplete/prefetch.json',
        ttl: 0
     },
     template: '<span style="color:#000;font-size:20px;font-weight:200;">{{value}}</span>',
     limit: 10,
     source: '',
     rateLimitWait: 170,
     updater : function(item) {
         //this.$element[0].value = item;
         //this.$element[0].form.submit();
         return item;
     },
     engine: Hogan
  }]).on('typeahead:selected', submit_query);



  //$('#query_main').typeahead({
  //  'updater' : function(item) {
  //      this.$element[0].value = item;
  //      this.$element[0].form.submit();
  //      return item;
  //  }
  //});

});


  /*
  var stream_list_JQ = $(".selected-streams-list");
  //This deletes the source from the list and deletes the source from the river
  stream_list_JQ.on("click", ".delete-stream-button", function() {
      //This grabs the id from the attribute data-id to use in $.post
      var stream_id = $(this).attr("data-id");
      //Removes stream from the river
      //FIX THIS line below, it is not DRY
      $(this).parent().parent().parent().parent().remove();
      //Deletes source from the river
      //The object e does not exist here, we need to find a replacement for it, or grab the domain
      if (source_count > 1) {
           $.post('/api/swapSource/', { domain: stream_id, intent: "remove" },
              function(response) {
                 news = jQuery.parseJSON(response.updated_news);
                 source_count -= 1;
                 // IMPORTANT: This code resets the select, so we cna
                 // delete something and reselect it!
                 $("#dropdown_sources").select2("val", "");
             }, 'json')
      } else {
          $('#stream-limit-warning-modal-min').modal('show');
      }
  });

  */
