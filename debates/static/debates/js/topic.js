function changesort() {
    var val = document.getElementById("sorts").value;
    Cookies.set("dsort", val, { expires: 30 });
    var x = window.location.search;
    var argindex = x.indexOf("&sort=");
    if (argindex != -1)
    {
      x = x.substring(0, x.indexOf("&sort="));
    }
    window.location.search = x + "&sort=" + val;
}
// IF arg is passed, cookie is NOT changed but arg takes priority
// IF drop down is changed, cookie is changed
//

window.onload = function () {
  var x = window.location.search.lastIndexOf("sort=");
  var b = window.location.search.indexOf("&", x);
  var c = Cookies.get("dsort");
  if (b == -1) {
    b = window.location.search.length;
  }
  if(x != -1) {
    document.getElementById("sorts").value = window.location.search.substring(x+5, b);
  } else if (c != null) {
    document.getElementById("sorts").value = c;
  }

};

$(document).ready(function() {

    $('.votebtn').click(function() {
      var id = $(this).parent().parent().parent().attr('data-debate-id');
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
      $.post($(this).parent().parent().parent().parent().attr('data-vote-url'), {id:id, vote:vote, csrfmiddlewaretoken:Cookies.get('csrftoken')}, function(response) {

        if(!isNaN(Number(response))){
          karmacount.html(response);
          console.log(response);
        }
      }, 'text');
    });
});
