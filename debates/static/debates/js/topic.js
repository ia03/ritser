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
