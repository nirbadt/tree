#include <Arduino.h>
#include <FastLED.H>
#include <Wire.h>
#include <SoftTimer.h>
#include <DelayRun.h>

#define I2C_ADDR  0x42
#define MAX_RECEIVED_BYTES  16

#define LED_DATA_PIN 6
#define NUM_LEDS 10

CRGB leds[NUM_LEDS];

void turnOn(Task* me) {
    leds[0] = CRGB::Red;
    FastLED.show();
}

void turnOff(Task* me) {
    leds[0] = CRGB::Black;
    FastLED.show();
}

DelayRun taskOff(200, turnOff);
DelayRun taskOn(200, turnOn, &taskOff);

void setup() {
    SoftTimer.add(&taskOn);
    SoftTimer.add(&taskOff);
    FastLED.addLeds<WS2811, LED_DATA_PIN, RGB>(leds, NUM_LEDS);
    Wire.begin(I2C_SENSOR_ADDRESS);
    Wire.onReceive(receiveData);

}