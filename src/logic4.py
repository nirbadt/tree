import Queue
import threading
import time
import BlynkLib
import Adafruit_MPR121.MPR121 as MPR121
import subprocess
import serial
import pygame
from os import path

import random
from subprocess import call

SERIAL_PORT = '/dev/ttyACM0'

PIXEL_COUNT = 240
GROWING_SPEED = 3
SHRINKING_SPEED = 6

#global remoteTouchCount
remoteTouchCount = 0

idle_start_time = time.time()

print('initializing serial')
ser = serial.Serial(SERIAL_PORT)
ser.baudrate = 115200
print('serial initialized')

#pygame.mixer.pre_init(44100, 16, 2, 4096) #frequency, size, channels, buffersize
#pygame.init() #turn all of pygame on.

my_sounds = ['my_01.wav','my_02.wav','my_03.wav','my_04.wav','my_05.wav','my_06.wav','my_07.wav','my_08.wav']
other_sounds = ['other_01.wav','other_02.wav','other_03.wav','other_04.wav','other_05.wav','other_06.wav','other_07.wav','other_08.wav','other_09.wav']
breath_sounds = ['breath_01.wav','breath_02.wav','breath_03.wav','breath_04.wav']

touchCount = 0

print('initializing sound')
pygame.mixer.init()
print('sound initialized')

MSG_TOUCH = 'touch'
MSG_RELEASE = 'release'
MSG_GOT_WIN = 'got_win'
MSG_GOT_INVITED = 'got_invited'
MSG_GOT_CHARGE_RELEASED = 'got_charge_released'
MSG_TICK = 'tick'

ST_STANDBY = 'standby'
ST_CHARGING = 'charging'
ST_CHARGED = 'charged'
ST_BEEN_INVITED = 'been_invited'
ST_WIN = 'win'

LED_STANDBY = '1'
LED_CHARGING = '2'
LED_CHARGED = '5'
LED_BEEN_INVITED = '5'
LED_WIN = '3'

CHARGE_RELEASE_TIME = 0.5
CHARGE_TIME = 7
TICK_TIME = 0.1

IDLE_TIME = 5

BLYNK_SERVER = '139.59.206.133'
BLYNK_AUTH = 'ac4b8c5b7ece4a23b60e62733cf6d6fc'

class State:
    def __init__(self):
        self.current = ST_STANDBY
        self.state_start_millis = None
        self.release_start_millis = None
        self.LED = 1

def send_message(message):
    #print ("Sending message: " + message + "\n")
    tree_id = get_tree_number()
    other_tree_id = tree_id ^ 1
    call(["curl", "http://" + BLYNK_SERVER + "/" + BLYNK_AUTH + "/update/V{0}?value={1}".format(other_tree_id, message)])

def millis():
    return time.time()

def to_state(state, new_state, LED_state):
    state.current = new_state
    print ("Changing state to " + new_state + "\n")
    state.release_start_millis = None
    state.state_start_millis = millis()

def play_sound(sound_file):
    pygame.mixer.music.load(path.join('sounds', sound_file))
    pygame.mixer.music.play()

def in_standby(state, message):
    if message == MSG_TOUCH:
        to_state(state, ST_CHARGING, LED_CHARGING)
        my_random = random.choice(my_sounds)
        play_sound(my_random)
    elif message == MSG_GOT_INVITED:
        to_state(state, ST_BEEN_INVITED, LED_BEEN_INVITED)
        other_random = random.choice(other_sounds)
        play_sound(other_random)

def in_charging(state, message):
    if message == MSG_RELEASE:
        to_state(state, ST_STANDBY, LED_STANDBY)
        pygame.mixer.music.stop()
    elif message == MSG_TICK:
        elapsed_time = millis() - state.state_start_millis
        if elapsed_time > CHARGE_TIME:
            to_state(state, ST_CHARGED, LED_CHARGED)
            other_random = random.choice(other_sounds)
            play_sound(other_random)
            send_message(MSG_GOT_INVITED)

    elif message == MSG_GOT_INVITED:
        to_state(state, ST_WIN, LED_WIN)
        play_sound('both_sound16.wav')

def in_charged(state, message):
    if message == MSG_RELEASE:
        state.release_start_millis = millis()
    elif message == MSG_GOT_WIN:
        to_state(state, ST_WIN, LED_WIN)
        play_sound('both_sound16.wav')
    elif message == MSG_GOT_INVITED:
        to_state(state, ST_WIN, LED_WIN)
        send_message(MSG_GOT_WIN)
        play_sound('both_sound16.wav')
    elif message == MSG_TICK:
        if state.release_start_millis:
            elapsed_time = millis() - state.release_start_millis
            print "elapsed time is" + elapsed_time +"\n"
            if elapsed_time > CHARGE_RELEASE_TIME:
                to_state(state, ST_STANDBY, LED_STANDBY)
                pygame.mixer.music.stop()
                state.release_start_millis = None
                send_message(MSG_GOT_CHARGE_RELEASED)

def in_been_invited(state, message):
    if message == MSG_TOUCH:
        to_state(state, ST_WIN, LED_WIN)
        play_sound('both_sound16.wav')
        send_message(MSG_GOT_WIN)
    elif message == MSG_GOT_WIN:
        to_state(state, ST_WIN, LED_WIN)
        play_sound('both_sound16.wav')
    elif message == MSG_GOT_CHARGE_RELEASED:
        to_state(state, ST_STANDBY, LED_STANDBY)
        pygame.mixer.music.stop()

def in_win(state, message):
    if message == MSG_RELEASE or message == MSG_GOT_CHARGE_RELEASED:
        to_state(state, ST_STANDBY, LED_STANDBY)
        send_message(MSG_GOT_CHARGE_RELEASED)
        pygame.mixer.music.stop()

def state_machine(q):
    state = State()
    last_state = ST_STANDBY
    while True:
        global touchCount
        send_message(touchCount)
        time.sleep(0.5)
        if state.current != last_state:
            print("Now in state: " + state.current + "\n")
            last_state = state.current

print('initializing blynk')
blynk = BlynkLib.Blynk(BLYNK_AUTH, server=BLYNK_SERVER)

@blynk.VIRTUAL_WRITE(0)
def v0_write_handler(value):
    global q
    if get_tree_number() == 0:
        #q.put(value)
        global remoteTouchCount
        remoteTouchCount = int(value)
        #print("V0 Got value: " + remoteTouchCount + "\n")

@blynk.VIRTUAL_WRITE(1)
def v1_write_handler(value):
    global q
    if get_tree_number() == 1:
        #q.put(value)
        global remoteTouchCount
        remoteTouchCount = int(value)
        #print("V1 Got value: " + remoteTouchCount + "\n")

def get_tree_number():
    host_name = str(subprocess.check_output(['hostname']))
    return 0 if 'papa' in host_name else 1

def blynk_thread():
    while(True):
        try:
            blynk.run()
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)

# initialize capacitive sensor
cap = MPR121.MPR121()
if not cap.begin(busnum=1):
    print('Error initializing MPR121.  Check your wiring!')
    sys.exit(1)
else:
    print('cap initialized')

tree_number = get_tree_number()
print("Tree number is: " + str(tree_number) + "\n");

q = Queue.Queue()

t = threading.Thread(target = state_machine, args = (q,))
t.daemon = True
t.start()

t = threading.Thread(target = blynk_thread)
t.daemon = True
t.start()

#previous_touched = False


last_tick = millis()
last_touched = False
last_remoteTouchCount = 0
inWinningState = False
#global remoteTouchCount

while True:
    touched = cap.is_touched(0)
    if touched:
      idle_start_time = millis() + 100000 # Not idle - setting it to future time
      if not last_touched:
        print 'local charging started'
        pygame.mixer.music.stop()
        my_random = random.choice(my_sounds)
        play_sound(my_random)
        
      touchCount = touchCount + GROWING_SPEED
      if touchCount > PIXEL_COUNT:
        touchCount = PIXEL_COUNT
    else:
      if last_touched:
        print 'local charging stopped'
        pygame.mixer.music.stop()
        #play_sound('my_sound16_reversed2.wav')

      if touchCount > 0 and touchCount <= SHRINKING_SPEED:
        print 'local discharging ended'
        pygame.mixer.music.fadeout(2000)
        idle_start_time = millis()
        #pygame.mixer.music.load("")
        #pygame.mixer.music.play()

      touchCount = touchCount - SHRINKING_SPEED
      if touchCount <= 0:
        touchCount = 0
    #send_message(touchCount)
    #global remoteTouchCount
    ser.write("{} {}".format(touchCount, remoteTouchCount))
    #print("{} {}".format(touchCount, remoteTouchCount))
    time.sleep(0.05)
    
    # other end incoming sound handling:
    # give preference to local interaction over remote interaction
    if touchCount == 0:
      #global remoteTouchCount
      if last_remoteTouchCount == 0 and remoteTouchCount > 0:
        print 'remote charging detected'
        pygame.mixer.music.stop()

        other_random = random.choice(other_sounds)
        play_sound(other_random)
      else:
        if last_remoteTouchCount > remoteTouchCount:
          pygame.mixer.music.fadeout(2000)
        
    # handle winning state
    #global remoteTouchCount
    if remoteTouchCount > 0:
      idle_start_time = millis() + 100000 # Not idle - setting it to future time
      if remoteTouchCount == PIXEL_COUNT and touchCount == PIXEL_COUNT:
        if not inWinningState:
          pygame.mixer.music.stop()
          play_sound('both_sound16.wav')
          inWinningState = True
      else:
        inWinningState = False


    if last_remoteTouchCount == PIXEL_COUNT and remoteTouchCount < PIXEL_COUNT:
      if touchCount == 0:
        pygame.mixer.music.fadeout(2000)
        idle_start_time = millis() # Setting idle state from remote touch
      else:
        pygame.mixer.music.stop()
        my_random = random.choice(my_sounds)
        play_sound(my_random)

    # Checking idle time
    # Every 10 seconds we play a new random idle sound
    since_idle_start = millis() - idle_start_time
    if since_idle_start > IDLE_TIME:
        print('Idle detected')
        idle_start_time = millis()
        idle_random = random.choice(breath_sounds)
        play_sound(idle_random)

#        last_tick = millis()
#        q.put(MSG_TICK)
#    previous_touched = touched
    last_touched = touched
    last_remoteTouchCount = remoteTouchCount
