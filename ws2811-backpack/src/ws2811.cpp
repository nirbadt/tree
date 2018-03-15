#include <FastLED.H>
#include "ws2811.h"
uint16_t frame = 0;			//I think I might be able to move this variable to the void loop() scope and save some CPU
uint16_t animateSpeed = 100; 
CRGB stripUp[NUM_LEDS];
CRGB stripDown[NUM_LEDS];
CRGB stripSnow[NUM_LEDS];
 
void tick() {
    FastLED.show();					//All animations are applied!..send the results to the strip(s)
	frame += animateSpeed;
    frame %= MAX_INT_VALUE;
}
void init_leds() {
    FastLED.addLeds<WS2811, 6, GRB>(stripUp, NUM_LEDS);
    FastLED.addLeds<WS2811, 5, GRB>(stripDown, NUM_LEDS);
    FastLED.addLeds<WS2811, 3, GRB>(stripSnow, NUM_LEDS);
}

void flashthumb() {    
    fill_solid(stripUp, NUM_LEDS, CHSV( 255, 0, 0) );
    fill_solid(stripDown, NUM_LEDS, CHSV( 0, 255, 0) );
    fill_solid(stripSnow, NUM_LEDS, CHSV( 0, 0, 255) );

    FastLED.show();
    delay(100);
    FastLED.clear();
    FastLED.show();
}

//********************************   Color Spark  ***********************************
// Color of the sparks is determined by "hue"
// Frequency of sparks is determined by global var "animateSpeed"
// "animateSpeed" var contrained from 1 - 255 (0.4% - 100%)
// "fade" parameter specifies dropoff (next frame brightness = current frame brightness * (x/256)
// fade = 256 means no dropoff, pixels are on or off
// NOTE: this animation doesnt clear the previous buffer because the fade/dropoff is a function of the previous LED state
//***********************************************************************************
void Spark(CRGB targetStrip[], uint16_t animationFrame,uint8_t fade, uint8_t hue){

	uint8_t stripLength = sizeof(targetStrip)/sizeof(CRGB);
	uint16_t rand = random16();

		for(int i=0;i<stripLength;i++)
		{		
			targetStrip[i].nscale8(fade);
		}


	if(rand < (MAX_INT_VALUE / (256 - (constrain(animateSpeed,1,256)))))	;
	{
		targetStrip[rand % stripLength].setHSV(hue,255,255);
	}
}

void drawFractionalBar(CRGB targetStrip[], int pos16, int width, uint8_t hue, bool wrap)
{
	uint8_t stripLength = sizeof(targetStrip)/sizeof(CRGB);
	uint8_t i = pos16 / 16; // convert from pos to raw pixel number

	uint8_t frac = pos16 & 0x0F; // extract the 'factional' part of the position
	uint8_t firstpixelbrightness = 255 - (frac * 16);
	
	uint8_t lastpixelbrightness = 255 - firstpixelbrightness;

	uint8_t bright;
	for (int n = 0; n <= width; n++) {
		if (n == 0) {
			// first pixel in the bar
			bright = firstpixelbrightness;
		}
		else if (n == width) {
			// last pixel in the bar
			bright = lastpixelbrightness;
		}
		else {
			// middle pixels
			bright = 255;
		}

		targetStrip[i] += CHSV(hue, 255, bright );
		i++;
		if (i == stripLength)
		{
			if (wrap == 1) {
				i = 0; // wrap around
			}
			else{
				return;
			}
		}
	}
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
        case PIXEL_UP: {
            drawFractionalBar(stripUp, frame, 5, CRGB(255, 0, 0), false);
            break;
        }
        case PIXEL_DOWN: {
            drawFractionalBar(stripDown, MAX_INT_VALUE-frame, 5, CRGB(0, 255, 0), false);
            break;
        }
        case PIXEL_SNOW: {
            Spark(stripSnow, frame, 100, CRGB(255, 255, 255));
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
            fill_solid(stripUp, NUM_LEDS, strip_color);
            fill_solid(stripDown, NUM_LEDS, strip_color);
            fill_solid(stripSnow, NUM_LEDS, strip_color);
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
            // color.fadeToBlackBy(255-brightness);
            // thumb[index] = color;
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
