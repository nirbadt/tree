
#ifndef WS2811_h
#define WS2811_h

#include <FastLED.H>
#define LED_DATA_PIN 6
#define NUM_LEDS 240

// pixel command instruction set
#define PIXEL_OFF               0x00 // set strip to be off
#define PIXEL_CONFIG            0x01 // DEPRECATED was setting pin and length
#define PIXEL_SHOW              0x02 // latch the pixels and show them
#define PIXEL_SET_PIXEL         0x03 // set the color value of pixel n using 32bit packed color value
#define PIXEL_SET_STRIP         0x04 // set color of whole strip
#define PIXEL_SHIFT             0x05 // shift all pixels n places along the strip

#define PIXEL_UP         0x06 // shift all pixels n places along the strip
#define PIXEL_DOWN       0x07 // shift all pixels n places along the strip
#define PIXEL_SNOW       0x08 // shift all pixels n places along the strip

#define MAX_INT_VALUE 65536

void tick();
void init_leds();
void flashthumb();
void process_command(byte argc, byte *argv);

#endif
