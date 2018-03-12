require('dotenv').config()

var five = require('johnny-five');
var pixel = require('node-pixel');
var Raspi = require('raspi-io');
var board = new five.Board({
    io: new Raspi()
});

board.on('ready', () => {
    const strip = new pixel.Strip({
        board,
        length: 5,
        address: parseInt(process.env.I2C_ADDRESS, 16),
        controller: 'I2CBACKPACK',
    })

    const touchpad = new five.Touchpad({ controller: 'MPR121' })
    strip.on('ready', () => {})
    touchpad.on('change', ({which}) => console.log(which))
    touchpad.on('press', ({which}) => console.log(which))
    touchpad.on('hold', ({which}) => console.log(which))
    touchpad.on('release', ({which}) => console.log(which))
});