var _settings = undefined;
var _canvas = undefined;

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
  _canvaiops.width = _settings.width * 2;
  _canvas.id = "canvas"
  _canvas.getContext("2d").scale(2, 2);

  document.getElementById("pixelboard").appendChild(_canvas);
  setTimeout(updateBoard, 0);
};

let updateBoard = function() {
  fetch("/pixels")
  .then((response) => response.json())
  .then((data) => {
    let ctx = _canvas.getContext("2d");
    let pixels = data.pixels;
    console.log(pixels);

    for (let y = 0; y < pixels.length; y++) {
      for (let x = 0; x < pixels[y].length; x++) {
        let paletteIndex = pixels[y][x];
        let color = _settings.palette[paletteIndex];

        ctx.fillStyle = color;
        ctx.fillRect(x, y, 1, 1);
      }
    }

    setTimeout(updateBoard, 20);
  })
};
