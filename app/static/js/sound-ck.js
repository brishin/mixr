// Load SoundManager
(function(e){"use strict";soundManager.setup({url:"/static/swf/",flashVersion:9,preferFlash:!1,debugMode:!1,onready:function(){playSong({title:"Upgrade you"});nowPlaying.play()}})})(document);var nowPlaying="",playSong=function(e){"use strict";$.post("https://mixr.herokuapp.com/api/play",{title:e.title},function(e){nowPlaying=soundManager.createSound({id:"nowPlaying",url:e.url,onload:function(){this.play()}})},"json")},getSongs=function(e){"use strict";$.post("https://mixr.herokuapp.com/api/random",{rows:e},function(e){return e},"json")},updateSliderValue=function(e,t){"use strict";var n=null;n=$(".ui-slider-handle",$("#volume"));if(t.value){$("#volume > div").text(t.value+"%").css(n.position());nowPlaying.setVolume(t.value)}};$("#volume").slider({animate:!0,step:1,min:0,value:50,max:100,slide:updateSliderValue,create:updateSliderValue});