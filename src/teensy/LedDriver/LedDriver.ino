// #define REDUCED_MODES // sketch is too big for Arduino w/32k flash, so invoke reduced modes
#include <WS2812FX.h>

#define STRIP_COUNT 3
#define STATE_COUNT 5

int LED_COUNT[STRIP_COUNT] = {24, 6, 240};
int LED_PINS[STRIP_COUNT] = {5, 4, 3};

// states: STANDBY, CHARGING, CHARGED, INVITING, WIN
int modes[][STRIP_COUNT] =   {{15, 15, 15},       {44, 3, 3},         {11, 11, 12}, {15, 15, 15},    {45, 33, 50}};
long speeds[][STRIP_COUNT] = {{6000, 6000, 6000}, {750, 1500, 15000}, {10, 10, 10}, {500, 500, 500}, {500, 250, 40000}};

WS2812FX strips[STRIP_COUNT] = {
  WS2812FX(LED_COUNT[0], LED_PINS[0], NEO_GRB + NEO_KHZ800),
  WS2812FX(LED_COUNT[1], LED_PINS[1], NEO_GRB + NEO_KHZ800),
  WS2812FX(LED_COUNT[2], LED_PINS[2], NEO_GRB + NEO_KHZ800)
};

void setup() {
  Serial.begin(9600);
  Serial1.begin(9600);
  for (int i = 0; i < STRIP_COUNT; ++i) {
    strips[i].init();
    strips[i].setBrightness(30);
    strips[i].setColor(0x007BFF);
  }
  Serial.println("Ready. your state is my command. or maybe the other way around. ~~~");
  Serial1.println("Ready. your state is my command. or maybe the other way around. ~~~");
}

void loop() {
  for (int i = 0; i < STRIP_COUNT; ++i) {
    strips[i].service();
  }
}

/*
   Reads new input from serial to cmd string. Command is completed on \n
*/
void serialEvent() {
  if (Serial.available()) {
    char inChar = (char) Serial.read();
    handleCommand(inChar);
    while (Serial.available()) {
      Serial.read();
    }
  }
}

void serialEvent1() {
  if (Serial1.available()) {
    char inChar = (char) Serial1.read();
    handleCommand(inChar);
    while (Serial.available()) {
      Serial.read();
    }
  }
}

void handleCommand(char inChar) {
  switch (inChar) {
    case '0':
      for (int i = 0; i < STRIP_COUNT; ++i) {
        // strips[i].setBrightness(30);
        // strips[i].setColor(0x007BFF);
        strips[i].setSpeed(100);
        strips[i].setMode(0);
        strips[i].strip_off();
        strips[i].stop();
      }
      break;
    case '1':
    case '2':
    case '3':
    case '4':
    case '5':
      int modee = inChar - '1';
      for (int i = 0; i < STRIP_COUNT; ++i) {
        // strips[i].setBrightness(30);
        // strips[i].setColor(0x007BFF);
        strips[i].setSpeed(speeds[modee][i]);
        strips[i].setMode(modes[modee][i]);
        strips[i].start();
      }
      break;
  }
}

