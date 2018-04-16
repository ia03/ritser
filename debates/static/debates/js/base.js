/* global $ */
/* global Cookies */

$(document).ready(function() {

    $('.votebtn').click(function() {
      var id = $(this).parent().attr('data-debate-id');
      var durl = $(this).parent().attr('data-vote-url');
      if ($(this).hasClass('arrow-up'))
      {
        var vote = 1;
        $(this).addClass('arrow-up-selected').removeClass('arrow-up');
        if ($(this).parent().find('.arrow-down-selected').length !== 0)
        {
          $(this).parent().find('.arrow-down-selected').addClass('arrow-down').removeClass('arrow-down-selected');
        }
      } else if ($(this).hasClass('arrow-down'))
      {
        var vote = -1;
        $(this).addClass('arrow-down-selected').removeClass('arrow-down');
        if ($(this).parent().find('.arrow-up-selected').length !== 0)
        {
          $(this).parent().find('.arrow-up-selected').addClass('arrow-up').removeClass('arrow-up-selected');
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
      $.post(durl, {id:id, vote:vote, csrfmiddlewaretoken:Cookies.get('csrftoken')}, function(response) {

        if(!isNaN(Number(response))){
          karmacount.html(response);
        }
      });
    });
    $('.savebtn').click(function() {
      var surl = $(this).attr('data-save-url');
      var id = $(this).attr('data-id');
      var typ = $(this).attr('data-typ');
      if ($(this).html() == 'Save')
      {
        var save = 0;
        $(this).html('Unsave');
      }
      else
      {
        var save = 1;
        $(this).html('Save');
      }
      
      $.post(surl, {id:id, typ:typ, save:save, csrfmiddlewaretoken:Cookies.get('csrftoken')});
      
    });
    
    
});
