// Load the SDK Asynchronously
(function(d){
   var js, id = 'facebook-jssdk', ref = d.getElementsByTagName('script')[0];
   if (d.getElementById(id)) {return;}
   js = d.createElement('script'); js.id = id; js.async = true;
   js.src = "//connect.facebook.net/en_US/all.js";
   ref.parentNode.insertBefore(js, ref);
 }(document));

// Init the SDK upon load
window.fbAsyncInit = function() {
  FB.init({
    appId      : '325013177591412', // App ID
    channelUrl : '//'+window.location.hostname+'/channel.html', // Path to your Channel File
    status     : true, // check login status
    cookie     : true, // enable cookies to allow the server to access the session
    xfbml      : true  // parse XFBML
  });

  // respond to clicks on the login and logout links
  document.getElementById('auth-loginlink').addEventListener('click', function(){
    FB.login();
  });
  document.getElementById('auth-logoutlink').addEventListener('click', function(){
    FB.logout();
  }); 

  FB.Event.subscribe('auth.statusChange', function(response) {
    if (response.authResponse) {
      // user has auth'd your app and is logged into Facebook
      var data = {'authkey': FB.getAccessToken(), 'userID': FB.getUserID()};
<<<<<<< HEAD
      $.post('https://'+window.location.hostname+'/api/login', data, function(){
=======
      $.post('https://'+window.location.hostname+'/login', data, function(){
>>>>>>> 71e2c04a354bf01574ba2d04aca470d2cec586bc
        document.getElementById('auth-loggedout').style.display = 'none';
        document.getElementById('auth-loggedin').style.display = 'block';
      });
    } else {
      // user has not auth'd your app, or is not logged into Facebook
      document.getElementById('auth-loggedout').style.display = 'block';
      document.getElementById('auth-loggedin').style.display = 'none';
    }
  });
} 