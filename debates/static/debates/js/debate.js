/* global $ */

window.onload = function () {
  var x = window.location.search.lastIndexOf("tab=");
  var b = window.location.search.indexOf("&", x);
  if (b == -1) {
    b = window.location.search.length;
  }
  if(x != -1 && window.location.search.substring(x+4, b) == "1") {
    document.getElementById("for-tab").className = "nav-link";
    document.getElementById("against-tab").className = "nav-link active show";
    document.getElementById("for").className = "tab-pane fade";
    document.getElementById("against").className = "tab-pane fade active show";
  }

};


$(document).ready(function() {

    $('.votebtn').click(function() {
      var id = $(this).parent().attr('data-debate-id');
      if ($(this).hasClass('arrow-up'))
      {
        var vote = 1;
        $(this).addClass('arrow-up-selected').removeClass('arrow-up');
        if ($(this).parent().find('.arrow-down-selected').length !== 0)
        {
          $(this).parent().find('.arrow-down-selected').addClass('arrow-down').removeClass('arrow-down-selected')
        }
      } else if ($(this).hasClass('arrow-down'))
      {
        var vote = -1;
        $(this).addClass('arrow-down-selected').removeClass('arrow-down');
        if ($(this).parent().find('.arrow-up-selected').length !== 0)
        {
          $(this).parent().find('.arrow-up-selected').addClass('arrow-up').removeClass('arrow-up-selected')
        }
      } else if ($(this).hasClass('arrow-up-selected'))
      {
        var vote = 0;
        $(this).addClass('arrow-up').removeClass('arrow-up-selected');
      } else if ($(this).hasClass('arrow-down-selected'))
      {
        var vote = 0;
        $(this).addClass('arrow-down').removeClass('arrow-down-selected');
      }
      var karmacount = $(this).parent().find('.karmacount');
      $.post($(this).parent().attr('data-vote-url'), {id:id, vote:vote, csrfmiddlewaretoken:Cookies.get('csrftoken')}, function(response) {

        if(!isNaN(Number(response))){
          karmacount.html(response);
          console.log(response);
        }
      }, 'text');
    });
    $('#for-tab').click(function () {
      var reExp = /tab=\d+/;
      var url = window.location.toString();
      var state = {tab:0};
      if (reExp.test(url))
      {
        history.pushState(state, '', url.replace(reExp, "tab=" + '0'));
      } else {
        if (window.location.search.indexOf('?') > -1)
        {
          history.pushState(state, '', window.location.search + "&tab=1");
        } else {
          history.pushState(state, '', window.location.search + "?tab=1");
        }
      }
    });
    $('#against-tab').click(function () {
      var reExp = /tab=\d+/;
      var url = window.location.toString();
      var state = {tab:1};
      if (reExp.test(url))
      {
        history.pushState(state, '', url.replace(reExp, "tab=" + '1'));
      } else {
        if (window.location.search.indexOf('?') > -1)
        {
          history.pushState(state, '', window.location.search + "&tab=1");
        } else {
          history.pushState(state, '', window.location.search + "?tab=1");
        }
      }
    });
});


$(window).on('popstate', function(event) {
    var state = event.originalEvent.state;

    if (state) {
        if (state.tab == 0)
        {
          document.getElementById("for-tab").className = "nav-link active show";
          document.getElementById("against-tab").className = "nav-link";
          document.getElementById("for").className = "tab-pane fade active show";
          document.getElementById("against").className = "tab-pane fade";
        }
        else if (state.tab == 1)
        {
          document.getElementById("for-tab").className = "nav-link";
          document.getElementById("against-tab").className = "nav-link active show";
          document.getElementById("for").className = "tab-pane fade";
          document.getElementById("against").className = "tab-pane fade active show";
        }
    }
});
