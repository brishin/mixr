// Load SoundManager
(function(d) {
  "use strict";
  soundManager.setup({
    url: '/static/swf/',
    flashVersion: 9,
    preferFlash: false,
    debugMode: false
  });
}(document));

var nowPlaying = "";

// Add sound based on bubble JSON
var playSong = function(song) {
  "use strict";
  $.post("http://localhost:5000/api/play", {
    'title': song.title
  }, function(data) {
    nowPlaying = soundManager.createSound({
      id: 'nowPlaying',
      url: data.url,
      onload: function() { this.play(); }
    });
  }, 'json');
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
