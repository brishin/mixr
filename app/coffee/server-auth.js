FB.Event.subscribe('auth.statusChange', function(response) {
  if (response.authResponse) {
    // user has auth'd your app and is logged into Facebook
    var authKey = FB.getAccessToken()
    var userID = FB.getUserID()
    $.post()
    document.getElementById('auth-loggedout').style.display = 'none';
    document.getElementById('auth-loggedin').style.display = 'block';
  } else {
    // user has not auth'd your app, or is not logged into Facebook
    document.getElementById('auth-loggedout').style.display = 'block';
    document.getElementById('auth-loggedin').style.display = 'none';
  }
});