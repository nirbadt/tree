#include <FastLED.H>
#include "ws2811.h"

CRGB thumb[NUM_LEDS];
CRGB index[NUM_LEDS];
CRGB middle[NUM_LEDS];
CRGB ring[NUM_LEDS];
CRGB pinky[NUM_LEDS];

void init_leds() {
    FastLED.addLeds<WS2811, LED_DATA_PIN, GRB>(thumb, NUM_LEDS);
}

void flashthumb() {    
    fill_solid(thumb, NUM_LEDS, CHSV( 224, 187, 255) );
    FastLED.show();
    delay(100);
    FastLED.clear();
    FastLED.show();
}

void process_command(byte argc, byte *argv){
    // this takes a pixel command that has been determined and then
    // processes it appropriately.

    uint8_t command = 0xF & argv[0];

    // now process the command.
    switch (command) {
        case PIXEL_OFF: {
            Serial.println("PIXEL_OFF");
            FastLED.clear();
            break;
        }
        case PIXEL_SHOW: {
            Serial.println("PIXEL_SHOW");
            FastLED.show();
            break;
        }
        case PIXEL_SET_STRIP: {
            CRGB strip_color = CRGB((uint32_t)argv[1] +
                ((uint32_t)argv[2]<<7) +
                ((uint32_t)argv[3]<<14) +
                ((uint32_t)argv[4] << 21));
            
            uint16_t brightness = (uint16_t)argv[5] + ((uint16_t)argv[6]<<7);
            
            strip_color.fadeToBlackBy(255-brightness);
            fill_solid(thumb, NUM_LEDS, strip_color);
            Serial.print("Set Strip ");
            Serial.print(brightness);
            Serial.print(" ");
            Serial.println(strip_color);
            break;
        }
        case PIXEL_SET_PIXEL: {
            // sets the pixel given by the index to the given colour
            uint16_t index = (uint16_t)argv[1] + ((uint16_t)argv[2]<<7);
            CRGB color = CRGB((uint32_t)argv[3] + ((uint32_t)argv[4]<<7) +
                ((uint32_t)argv[5]<<14) + ((uint32_t)argv[6] << 21));

            uint16_t brightness = (uint16_t)argv[7] + ((uint16_t)argv[8]<<7);
            color.fadeToBlackBy(255-brightness);
            thumb[index] = color;
            Serial.print("Set pixel ");
            Serial.print(brightness);
            Serial.print(" ");
            Serial.print(index);
            Serial.print(" ");
            Serial.println(color);
            break;
        }
        case PIXEL_CONFIG: {
            
            break;
        }
        case PIXEL_SHIFT: {

            break;
        }
    }
}
