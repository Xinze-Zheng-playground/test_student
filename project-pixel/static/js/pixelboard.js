var _settings = undefined;
var _canvas = undefined;
var _netid = undefined;
var _netidText = undefined;
var _enableToken = undefined;
var _colorChoice = undefined;
var _previousChoice = undefined;
// Fetch the settings:
fetch("/settings")
.then((response) => response.json())
.then((settings) => {
  _settings = settings;
  initBoard();
})



// Initialize the canvas:
let initBoard = function() {
  _canvas = document.createElement("canvas");
  _canvas.height = _settings.height * 2;
  _canvas.width = _settings.width * 2;
  _canvas.id = "canvas"
  _canvas.getContext("2d").scale(2, 2);
  _canvas.addEventListener('click', function(event) {
    if(_netid === undefined || _colorChoice === undefined) {
      return;
    }
    var elem = document.getElementById('canvas'),
    elemLeft = elem.offsetLeft + elem.clientLeft,
    elemTop = elem.offsetTop + elem.clientTop,
    y = parseInt(event.pageX - elemLeft),
    x = parseInt(event.pageY - elemTop);
    fetch(`/changeByClick/${x}/${y}/${_colorChoice}/${_netid}/`)
  }, false);

  _enableToken = document.getElementById("enable")
  _enableToken.addEventListener('click', function(event){
    _netid = document.getElementById("netid").value
  }, false);

  // Initialize the color selector
  var colorSelect = document.getElementById("selector")
  for(var i = 0; i < _settings.palette.length; i++) {
    var option = document.createElement("div")
    option.style.backgroundColor = _settings.palette[i]
    option.setAttribute('value', i)
    option.style.height = '20px'
    option.style.width = (80/_settings.palette.length) + '%'
    option.style.display = 'inline-block'
    option.addEventListener('click', function(event) {
      if(_previousChoice !== undefined) {
        _previousChoice.style.outline = ''
      }

      _colorChoice = event.target.getAttribute("value")
      event.target.style.outline = "solid blue 3px";
      _previousChoice = event.target;
    })
    colorSelect.append(option)
  }
  document.getElementById("pixelboard").appendChild(_canvas);
  setTimeout(updateBoard, 0);
};


let updateBoard = function() {
  fetch("/pixels")
  .then((response) => response.json())
  .then((data) => {
    let ctx = _canvas.getContext("2d");
    let pixels = data.pixels;

    for (let y = 0; y < pixels.length; y++) {
      for (let x = 0; x < pixels[y].length; x++) {
        let paletteIndex = pixels[y][x];
        let color = _settings.palette[paletteIndex];

        ctx.fillStyle = color;
        ctx.fillRect(x, y, 1, 1);
      }
    }

    setTimeout(updateBoard, 1000);
  })
};
