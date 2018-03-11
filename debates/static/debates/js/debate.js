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
});
