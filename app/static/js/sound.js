// Load SoundManager
(function(d) {
  "use strict";
  soundManager.setup({
    url: '/static/swf/',
    flashVersion: 9,
    preferFlash: false,
    debugMode: false,
    onready: function() {
      playSong({'title': "Upgrade you"});
      nowPlaying.play();
    }
  });
}(document));

var nowPlaying = "";

// Add sound based on bubble JSON
var playSong = function(song) {
  "use strict";
  $.post("https://jubble.herokuapp.com/api/play", {
    'title': song.title
  }, function(data) {
    nowPlaying = soundManager.createSound({
      id: 'nowPlaying',
      url: data.url,
      onload: function() { this.play(); }
    });
  }, 'json');
};

var getSongs = function(num) {
  "use strict";
  var a;
  $.post("https://jubble.herokuapp.com/api/random", {
    'rows': num
  }, function(data) {a = data;}, 'json');
  return a;
};

var updateSliderValue = function(event, ui) {
  "use strict";
  var handle = null;
  handle = $(".ui-slider-handle", $("#volume"));
  if(ui.value) {
    $("#volume > div").text(ui.value + "%").css(handle.position());
    nowPlaying.setVolume(ui.value);
  }
};

$("#volume").slider({
  animate: true,
  step: 1,
  min: 0,
  value: 50,
  max: 100,
  slide: updateSliderValue,
  create: updateSliderValue
});
