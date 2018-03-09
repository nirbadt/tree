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
            uint32_t strip_color = (uint32_t)argv[1] +
                ((uint32_t)argv[2]<<7) +
                ((uint32_t)argv[3]<<14) +
                ((uint32_t)argv[4] << 21);
            // fill_solid(thumb, NUM_LEDS, CHSV( 224, 187, 255) );
            // sets the entirety of the strip to one colour
            fill_solid(thumb, NUM_LEDS, strip_color);
            Serial.print("Set Strip ");
            Serial.println(strip_color);
            break;
        }
        case PIXEL_SET_PIXEL: {
            // sets the pixel given by the index to the given colour
            uint16_t index = (uint16_t)argv[1] + ((uint16_t)argv[2]<<7);
            uint32_t color = (uint32_t)argv[3] + ((uint32_t)argv[4]<<7) +
                ((uint32_t)argv[5]<<14) + ((uint32_t)argv[6] << 21);

            thumb[index] = color;
            
            Serial.print("Set pixel ");
            Serial.print(index);
            Serial.print(" ");
            Serial.println(color);
            break;
        }
        case PIXEL_CONFIG: {
            // Sets the pin that the strip is on as well as it's length and color type

            if (argv[0] > 0x01) {
                // you get a weird boundary case in I2C where sometimes a message
                // is relayed from firmata without the command packet.
                // Just ignore this and move along
                break;
            }
            
            // check to ensure we have at least 3 arg bytes (1 for pin & 2 for len)
            // if (argc >= 3) {
            //     for (uint8_t i = 0; i < (argc / 3); i ++) {
            //         // calc the argv offset as x3 for each group & +1 due to the
            //         // PIXEL_CONFIG command at argv[0]
            //         uint8_t argv_offset = i * 3;

            //         if (!isBackpack) {
            //             // we can specify the pin, otherwise it's determined.
            //             uint8_t pin = (uint8_t)argv[argv_offset+1] & 0x1F;
            //             strips[i].setOutput(pin);
            //         }

            //         // get the top two bits for the colour order type.
            //         uint8_t colour_type = (uint8_t)argv[argv_offset+1]>>5;
            //         switch (colour_type) {
            //             case PIXEL_COLOUR_GRB:
            //                 setColorOrderGRB();
            //                 break;
            //             case PIXEL_COLOUR_RGB:
            //                 setColorOrderRGB();
            //                 break;
            //             case PIXEL_COLOUR_BRG:
            //                 setColorOrderBRG();
            //                 break;
            //         }

            //         // now get the strand length and set it
            //         strips[i].set_length((uint16_t)(argv[argv_offset+2]+(argv[argv_offset+3]<<7)));
            //         uint16_t prev_strip_length = 0;
            //         if (i > 0) {
            //             prev_strip_length = strip_lengths[i-1];
            //         }
            //         strip_lengths[i] = strips[i].get_length() + prev_strip_length;
            //         // set the strip's offset so it knows where it is in the
            //         // 1D pixel array
            //         strips[i].set_offset(prev_strip_length);
            //         px_count = px_count + strips[i].get_length();

            //         strip_count++;
            //     }
               
            //}
            break;
        }// end config case
        case PIXEL_SHIFT: {

            break;
        }
    }
    // 
}
