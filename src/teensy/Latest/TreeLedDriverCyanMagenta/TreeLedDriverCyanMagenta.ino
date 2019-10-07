#include <WS2812FX.h>

#define LED_CHANNELS 5
#define STRIP_LEN 240

#define RING 0
#define FINGERS 1
#define STRIP_RAINBOW 2
#define STRIP_INCOMING 3
#define STRIP_OUTGOING 4


#define RING_WIDTH 12

#define MODE_OFF -1
#define MODE_STBY 0
#define MODE_ACTIVE 1
#define MODE_WINNING 2

#define MIN_COMPLETION_VALUE 0
#define MAX_COMPLETION_VALUE STRIP_LEN


// order: ring, fingers, strip rainbow, strip incoming, strip outgoing

int LED_COUNT[LED_CHANNELS] = {24, 6, 240, 240, 240};
int LED_PINS[LED_CHANNELS] = {5, 4, 3, 6, 7};


//                           STBY                              ACTIVE                           WINNING
int modes[][LED_CHANNELS] =   {{15, 15, 0, 0, 0},               {44, 3, 0, 0, 0},                {11, 11, 12, 12, 12}};
long speeds[][LED_CHANNELS] = {{6000, 6000, 6000, 6000, 6000}, {750, 1500, 15000, 15000, 15000}, {10, 10, 10, 10, 10}};
int _stripMode = MODE_OFF;

int _local = 0;
int _last_local = 0;
int _last_modes[LED_CHANNELS] = { -1};
int _remote = 0;
int effectCounter = 0;

WS2812FX strips[LED_CHANNELS] = {
  WS2812FX(LED_COUNT[RING], LED_PINS[RING], NEO_GRB + NEO_KHZ800),
  WS2812FX(LED_COUNT[FINGERS], LED_PINS[FINGERS], NEO_GRB + NEO_KHZ800),
  WS2812FX(LED_COUNT[STRIP_RAINBOW], LED_PINS[STRIP_RAINBOW], NEO_GRB + NEO_KHZ800),
  WS2812FX(LED_COUNT[STRIP_INCOMING], LED_PINS[STRIP_INCOMING], NEO_GRB + NEO_KHZ800),
  WS2812FX(LED_COUNT[STRIP_OUTGOING], LED_PINS[STRIP_OUTGOING], NEO_GRB + NEO_KHZ800)
};

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(5);
  for (int i = 0; i < LED_CHANNELS; ++i) {
    strips[i].init();
    strips[i].setBrightness(30);
    strips[i].setColor(0x00FFFF);//Cyan
    // strips[i].setColor(0xFF00FF);//Magenta
  }
  Serial.println("Ready. your indices are my command. or maybe the other way around. ~~~");
}

int localEffect = 0;
int remoteIndex = 0;

void loop() {
  for (int i = 0; i < LED_CHANNELS; ++i) {
    if (strips[i].isRunning()) {
      strips[i].service();
    }
    else {
      for (int i = 0; i < _local; ++i) {
        updateLocalVirtualPixelColor(i, strips[0].Color(0,255,255));//Cyan 
        // updateLocalVirtualPixelColor(i, strips[0].Color(255,0,255));//Magenta 
      }
      int localStart = constrain(localEffect - RING_WIDTH / 2, 0, _local);
      int localEnd = constrain(localEffect + RING_WIDTH / 2, 0, _local);
      for (int i = localStart ; i < localEnd ; ++i) {
        int intensity = constrain((i - localStart) * 10, 0, 255);
        updateLocalVirtualPixelColor(i, strips[0].Color(intensity, intensity, intensity));
      }
      for (int i = _local; i < STRIP_LEN; ++i) {
        updateLocalVirtualPixelColor(i, 0);
      }
      for (int i = 0; i < _remote; ++i) {
        // updateLocalVirtualPixelColor(i, strips[0].Color(0,255,255));//Cyan 
        updateRemoteVirtualPixelColor(i, strips[0].Color(255, 0, 255)); //Magenta 
      }
      int remoteStart = constrain(remoteIndex - RING_WIDTH / 2, 0, _remote);
      int remoteEnd = constrain(remoteIndex + RING_WIDTH / 2, 0, _remote);
      for (int i = remoteStart ; i < remoteEnd ; ++i) {
        int intensity = constrain(((i - remoteStart) < RING_WIDTH / 2) ? (i - remoteStart) * 10 : 255 - (i - remoteStart) * 10, 0, 255);
        // Serial.print(String(intensity) + "\t");
        updateRemoteVirtualPixelColor(i, strips[0].Color(intensity, intensity, intensity));
      }
      for (int i = _remote; i < STRIP_LEN; ++i) {
        updateRemoteVirtualPixelColor(i, 0);
      }

      strips[STRIP_RAINBOW].show();
      strips[STRIP_INCOMING].show();
      strips[STRIP_OUTGOING].show();

      if (effectCounter++ % 3 == 0) {
        localEffect = (localEffect + 1) % _local;
        remoteIndex = (remoteIndex + 1) % _remote;
      }
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

void setStripMode(int modee) {
  _stripMode = modee;
  if (modee == MODE_OFF) {
    for (int i = 0; i < LED_CHANNELS; ++i) {
      strips[i].setSpeed(100);
      strips[i].setMode(0);
      strips[i].strip_off();
      strips[i].stop();
    }
  }
  else {
    for (int i = 0; i < LED_CHANNELS; ++i) {
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

void updateLocalVirtualPixelColor(int idx, uint32_t col) {
  strips[STRIP_OUTGOING].setPixelColor(idx, col);
}

void updateRemoteVirtualPixelColor(int idx, uint32_t col) {
  strips[STRIP_INCOMING].setPixelColor(STRIP_LEN - 1 - idx, col);
}