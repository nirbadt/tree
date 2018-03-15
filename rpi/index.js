require('dotenv').config()

var five = require('johnny-five');
var Raspi = require('raspi-io');
var board = new five.Board({
    io: new Raspi()
});

board.on('ready', function() {
    
    const touchpad = new five.Touchpad({ controller: 'MPR121' })
    
    touchpad.on('change', ({which}) => console.log(which))
    touchpad.on('press', ({which}) => console.log(which))
    touchpad.on('hold', ({which}) => console.log(which))
    touchpad.on('release', ({which}) => console.log(which))

    var write = (message) => {
        this.io.i2cWrite(0x45, Array.from(message, c => c.charCodeAt(0)));
    };
    this.io.i2cConfig({address: 0x45});
    //write([0x06]);
    this.repl.inject({ write });
});