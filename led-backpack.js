var five = require('johnny-five');
var pixel = require('node-pixel');
var Raspi = require('raspi-io');
var board = new five.Board({
  io: new Raspi()
});

var fps = 60;

board.on('ready', function() {

    var strip = new pixel.Strip({
        address: 0x46,
        data: 6,
        length: 5,
        board: this,
        controller: 'I2CBACKPACK'
    });

    strip.on('ready', function() {

        var colors = ['magenta', 'blue']

        var blinker = setInterval(function() {
            const current = colors.pop()
            strip.color(current)
            colors.unshift(current)
        
            strip.show()
        }, 200)
    });
});
