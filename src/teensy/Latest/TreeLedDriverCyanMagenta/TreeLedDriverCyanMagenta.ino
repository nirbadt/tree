// #define REDUCED_MODES // sketch is too big for Arduino w/32k flash, so invoke reduced modes
#include <WS2812FX.h>

#define STRIP_COUNT 3
#define VIRTUAL_STRIP_LENGTH 240
#define VIRTUAL_STRIP_INDEX 2
#define RING_WIDTH 12

#define MODE_OFF -1
#define MODE_STBY 0
#define MODE_ACTIVE 1
#define MODE_WINNING 2

#define MIN_COMPLETION_VALUE 0
#define MAX_COMPLETION_VALUE VIRTUAL_STRIP_LENGTH

int LED_COUNT[STRIP_COUNT] = {24, 6, 240};
int LED_PINS[STRIP_COUNT] = {5, 4, 3};

// order: ring, fingers, stems
//                             STBY               ACTIVE               WINNING
int modes[][STRIP_COUNT] =   {{15, 15, 0},        {44, 3, 0},         {11, 11, 12}};
long speeds[][STRIP_COUNT] = {{6000, 6000, 6000}, {750, 1500, 15000}, {10, 10, 10}};
int _stripMode = MODE_OFF;

int _local = 0;
int _last_local = 0;
int _last_modes[STRIP_COUNT] = { -1};
int _remote = 0;
int effectCounter = 0;

WS2812FX strips[STRIP_COUNT] = {
  WS2812FX(LED_COUNT[0], LED_PINS[0], NEO_GRB + NEO_KHZ800),
  WS2812FX(LED_COUNT[1], LED_PINS[1], NEO_GRB + NEO_KHZ800),
  WS2812FX(LED_COUNT[2], LED_PINS[2], NEO_GRB + NEO_KHZ800)
};

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(5);
  Serial1.begin(9600);
  for (int i = 0; i < STRIP_COUNT; ++i) {
    strips[i].init();
    strips[i].setBrightness(30);
    strips[i].setColor(0x00FFFF);//Cyan
  }
  Serial.println("Ready. your indices are my command. or maybe the other way around. ~~~");
  Serial1.println("Ready. your indices are my command. or maybe the other way around. ~~~");
}

int localVirtualEffectIndex = 0;
int remoteVirtualEffectIndex = 0;

void loop() {
  for (int i = 0; i < STRIP_COUNT; ++i) {
    if (strips[i].isRunning()) {
      //      Serial1.println(String(i) + " is running");
      strips[i].service();
    }
    else {
      //for(int i = 0; i < VIRTUAL_STRIP_LENGTH; ++i) {
      for (int i = 0; i < _local; ++i) {
        updateLocalVirtualPixelColor(i, strips[0].Color(0,255,255));//Cyan 
      }
      int localStart = constrain(localVirtualEffectIndex - RING_WIDTH / 2, 0, _local);
      int localEnd = constrain(localVirtualEffectIndex + RING_WIDTH / 2, 0, _local);
      for (int i = localStart ; i < localEnd ; ++i) {
        // int intensity = constrain(((i - localStart) < RING_WIDTH/2) ? (i-localStart) * 10 : 255 - (i-localStart) * 10, 0, 255);
        int intensity = constrain((i - localStart) * 10, 0, 255);
        updateLocalVirtualPixelColor(i, strips[0].Color(intensity, intensity, intensity));
      }
      for (int i = _local; i < VIRTUAL_STRIP_LENGTH; ++i) {
        updateLocalVirtualPixelColor(i, 0);
      }
      for (int i = 0; i < _remote; ++i) {
        updateRemoteVirtualPixelColor(i, strips[0].Color(255, 0, 255)); //Magenta 
      }
      int remoteStart = constrain(remoteVirtualEffectIndex - RING_WIDTH / 2, 0, _remote);
      int remoteEnd = constrain(remoteVirtualEffectIndex + RING_WIDTH / 2, 0, _remote);
      for (int i = remoteStart ; i < remoteEnd ; ++i) {
        int intensity = constrain(((i - remoteStart) < RING_WIDTH / 2) ? (i - remoteStart) * 10 : 255 - (i - remoteStart) * 10, 0, 255);
        // Serial.print(String(intensity) + "\t");
        updateRemoteVirtualPixelColor(i, strips[0].Color(intensity, intensity, intensity));
      }
      for (int i = _remote; i < VIRTUAL_STRIP_LENGTH; ++i) {
        updateRemoteVirtualPixelColor(i, 0);
      }
      strips[VIRTUAL_STRIP_INDEX].show();
      if (effectCounter++ % 3 == 0) {
        localVirtualEffectIndex = (localVirtualEffectIndex + 1) % _local;
        remoteVirtualEffectIndex = (remoteVirtualEffectIndex + 1) % _remote;
      }
      //      }
    }
  }
}

/*
   Reads new input from serial to cmd string. Command is completed on \n
*/
void serialEvent() {
  if (Serial.available()) {
    int local = Serial.parseInt();
    int remote = Serial.parseInt();
    handleCommand(local, remote);
    while (Serial.available()) {
      Serial.read();
      delay(5);
    }
  }
}

//void serialEvent1() {
//  if (Serial1.available()) {
//    char inChar = (char) Serial1.read();
//    handleCommand(inChar);
//    while (Serial.available()) {
//      Serial.read();
//    }
//  }
//}
boolean isActive = false;

void handleCommand(int local, int remote) {
  _last_local = _local;
  _local = local;
  _remote = remote;
  if (local == MIN_COMPLETION_VALUE && remote == MIN_COMPLETION_VALUE) {
    setStripMode(MODE_STBY);
  }
  else if (local == MAX_COMPLETION_VALUE && remote == MAX_COMPLETION_VALUE) {
    setStripMode(MODE_WINNING);
  }
  else if (local > MIN_COMPLETION_VALUE || remote > MIN_COMPLETION_VALUE) {
    setStripMode(MODE_ACTIVE);
  }
}

void setStripMode(int modee, boolean updateVirtual) {
  _stripMode = modee;
  //  Serial1.println(String("setStripMode: ") + modee + ", virtual: " + updateVirtual);
  if (modee == MODE_OFF) {
    for (int i = 0; i < STRIP_COUNT; ++i) {
      // strips[i].setBrightness(30);
      // strips[i].setColor(0x007BFF);
      strips[i].setSpeed(100);
      strips[i].setMode(0);
      strips[i].strip_off();
      strips[i].stop();
      //      _last_modes[i] = modes[modee][i];
    }
  }
  else {
    for (int i = 0; i < STRIP_COUNT; ++i) {
      if (/* modes[modee][i] && */ _last_modes[i] != modes[modee][i]) {
        strips[i].setSpeed(speeds[modee][i]);
        strips[i].setMode(modes[modee][i]);
        if(modes[modee][i]) {
          strips[i].start();
        }
        else {
          strips[i].stop();
        }
        _last_modes[i] = modes[modee][i];
      }
    }
  }
}

void setStripMode(int modee) {
  setStripMode(modee, true);
}

void updateLocalVirtualPixelColor(int idx, uint32_t col) {
  strips[VIRTUAL_STRIP_INDEX].setPixelColor(idx - idx % 2, col);
}

void updateRemoteVirtualPixelColor(int idx, uint32_t col) {
  strips[VIRTUAL_STRIP_INDEX].setPixelColor(VIRTUAL_STRIP_LENGTH - 1 - (idx - idx % 2), col);
}


