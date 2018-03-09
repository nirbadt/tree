var five = require('johnny-five');
var pixel = require('node-pixel');
// var Raspi = require('raspi-io');
var board = new five.Board({
    port: '/dev/tty.wchusbserial14140'
//   io: new Raspi()
});
board.on('ready', function() {
    strip = new pixel.Strip({
        board: this,
        length: 5,
        address: 0x45,
        controller: 'I2CBACKPACK',
    });

    strip.on('ready', () => {
        console.log('strip ready')
        this.repl.inject({
            // Allow limited on/off control access to the
            // Led instance from the REPL.
           strip
          });
        // do stuff with the strip here.
        strip.color('#00ff00'); // turns entire strip red using a hex colour
        strip.show();
    });     
});