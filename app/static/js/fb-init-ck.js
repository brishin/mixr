// Load the SDK Asynchronously
(function(e){"use strict";var t,n="facebook-jssdk",r=e.getElementsByTagName("script")[0];if(e.getElementById(n))return;t=e.createElement("script");t.id=n;t.async=!0;t.src="//connect.facebook.net/en_US/all.js";r.parentNode.insertBefore(t,r)})(document);window.fbAsyncInit=function(){"use strict";FB.init({appId:"325013177591412",channelUrl:"/channel.html",status:!0,cookie:!0,xfbml:!0});document.getElementById("auth-loginlink").addEventListener("click",function(){FB.login(function(e){},{scope:"user_actions.music,friends_actions.music"})});document.getElementById("auth-logoutlink").addEventListener("click",function(){FB.logout()});FB.Event.subscribe("auth.statusChange",function(e){if(e.authResponse){var t={authKey:FB.getAccessToken(),userID:FB.getUserID()};$.post("https://"+window.location.hostname+"/api/login",t,function(){document.getElementById("auth-loggedout").style.display="none";document.getElementById("auth-loggedin").style.display="block"})}else{document.getElementById("auth-loggedout").style.display="block";document.getElementById("auth-loggedin").style.display="none"}})};