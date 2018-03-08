var five = require('johnny-five');
var pixel = require('node-pixel');
var Raspi = require('raspi-io');
var board = new five.Board({
  io: new Raspi()
});
board.on("ready", function() {
    strip = new pixel.Strip({
        board: this,
        address: 0x45,
        controller: "I2CBACKPACK",
        strips: [6], // 3 physical strips on pins 0, 1 & 2 with lengths 4, 6 & 8.
    });

    strip.on("ready", function() {
        console.log('strip ready')
        // do stuff with the strip here.
        strip.color("#ff0000"); // turns entire strip red using a hex colour
        strip.show();
    });     
});