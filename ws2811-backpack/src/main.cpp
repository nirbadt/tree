#include "defines.h"
#include "ws2811.h"

void receiveData(int numbytes) {
    byte received_bytes[MAX_RECEIVED_BYTES];

    for (uint8_t i=0; i < numbytes; i++) {
        if (i < MAX_RECEIVED_BYTES) {
                received_bytes[i] = Wire.read();
        } else {
                Wire.read();
        }
    }

    process_command(numbytes, received_bytes);
}

void setup() {
    Serial.begin(9600);
    init_leds();
    flashthumb();
    Wire.begin(I2C_ADDR);
    Wire.onReceive(receiveData);
}

void loop() {
    // Serial.println("loop");
    delay(1);
}