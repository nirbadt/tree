#include <WS2812FX.h>

#define STRIP_COUNT 5
#define VIRTUAL_STRIP_LENGTH 240


#define VIRTUAL_STRIP_RAINBOW_INDEX 2
#define VIRTUAL_STRIP_INCOMING_INDEX 3
#define VIRTUAL_STRIP_OUTGOING_INDEX 4


#define RING_WIDTH 12

#define MODE_OFF -1
#define MODE_STBY 0
#define MODE_ACTIVE 1
#define MODE_WINNING 2

#define MIN_COMPLETION_VALUE 0
#define MAX_COMPLETION_VALUE VIRTUAL_STRIP_LENGTH


// order: ring, fingers, strip rainbow, strip incoming, strip outgoing

int LED_COUNT[STRIP_COUNT] = {24, 6, 240, 240, 240};
int LED_PINS[STRIP_COUNT] = {5, 4, 3, 6, 7};


//                           STBY                              ACTIVE                           WINNING
int modes[][STRIP_COUNT] =   {{15, 15, 0, 0, 0},               {44, 3, 0, 0, 0},                {11, 11, 12, 12, 12}};
long speeds[][STRIP_COUNT] = {{6000, 6000, 6000, 6000, 6000}, {750, 1500, 15000, 15000, 15000}, {10, 10, 10, 10, 10}};
int _stripMode = MODE_OFF;

int _local = 0;
int _last_local = 0;
int _last_modes[STRIP_COUNT] = { -1};
int _remote = 0;
int effectCounter = 0;

WS2812FX strips[STRIP_COUNT] = {
  WS2812FX(LED_COUNT[0], LED_PINS[0], NEO_GRB + NEO_KHZ800),
  WS2812FX(LED_COUNT[1], LED_PINS[1], NEO_GRB + NEO_KHZ800),
  WS2812FX(LED_COUNT[VIRTUAL_STRIP_RAINBOW_INDEX], LED_PINS[VIRTUAL_STRIP_RAINBOW_INDEX], NEO_GRB + NEO_KHZ800),
  WS2812FX(LED_COUNT[VIRTUAL_STRIP_INCOMING_INDEX], LED_PINS[VIRTUAL_STRIP_INCOMING_INDEX], NEO_GRB + NEO_KHZ800),
  WS2812FX(LED_COUNT[VIRTUAL_STRIP_OUTGOING_INDEX], LED_PINS[VIRTUAL_STRIP_OUTGOING_INDEX], NEO_GRB + NEO_KHZ800)
};

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(5);
  for (int i = 0; i < STRIP_COUNT; ++i) {
    strips[i].init();
    strips[i].setBrightness(30);
    // strips[i].setColor(0x00FFFF);//Cyan
    strips[i].setColor(0xFF00FF);//Magenta
  }
  Serial.println("Ready. your indices are my command. or maybe the other way around. ~~~");
}

int localVirtualEffectIndex = 0;
int remoteVirtualEffectIndex = 0;

void loop() {
  for (int i = 0; i < STRIP_COUNT; ++i) {
    if (strips[i].isRunning()) {
      strips[i].service();
    }
    else {
      for (int i = 0; i < _local; ++i) {
        // updateLocalVirtualPixelColor(i, strips[0].Color(0,255,255));//Cyan 
        updateLocalVirtualPixelColor(i, strips[0].Color(255,0,255));//Magenta 
      }
      int localStart = constrain(localVirtualEffectIndex - RING_WIDTH / 2, 0, _local);
      int localEnd = constrain(localVirtualEffectIndex + RING_WIDTH / 2, 0, _local);
      for (int i = localStart ; i < localEnd ; ++i) {
        int intensity = constrain((i - localStart) * 10, 0, 255);
        updateLocalVirtualPixelColor(i, strips[0].Color(intensity, intensity, intensity));
      }
      for (int i = _local; i < VIRTUAL_STRIP_LENGTH; ++i) {
        updateLocalVirtualPixelColor(i, 0);
      }
      for (int i = 0; i < _remote; ++i) {
        updateLocalVirtualPixelColor(i, strips[0].Color(0,255,255));//Cyan 
        // updateRemoteVirtualPixelColor(i, strips[0].Color(255, 0, 255)); //Magenta 
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
      strips[VIRTUAL_STRIP_RAINBOW_INDEX].show();
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
  if (modee == MODE_OFF) {
    for (int i = 0; i < STRIP_COUNT; ++i) {
      strips[i].setSpeed(100);
      strips[i].setMode(0);
      strips[i].strip_off();
      strips[i].stop();
    }
  }
  else {
    for (int i = 0; i < STRIP_COUNT; ++i) {
      if ( _last_modes[i] != modes[modee][i]) {
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
  strips[VIRTUAL_STRIP_OUTGOING_INDEX].setPixelColor(idx, col);
}

void updateRemoteVirtualPixelColor(int idx, uint32_t col) {
  strips[VIRTUAL_STRIP_INCOMING_INDEX].setPixelColor(idx, col);
}