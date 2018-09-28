import BlynkLib
import pygame
import Queue
import threading
import time
import traceback

from os import path
import math

from subprocess import call

PIXEL_COUNT = 240
GROWING_SPEED = 3
SHRINKING_SPEED = 6

TREE_TO_TEST = 0 # TODO: Replace to 1 if you are testing the other tree

#global remoteTouchCount
remoteTouchCount = 0

print('Initialize')

touchCount = 0

print('initializing sound')
#pygame.mixer.pre_init(44100, 16, 2, 4096) #frequency, size, channels, buffersize
pygame.mixer.init()
print('sound initialized')

pygame.mixer.music.load(path.join("sounds","other_1.wav"))
pygame.mixer.music.play()

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

BLYNK_SERVER = '139.59.206.133'
BLYNK_AUTH = 'ac4b8c5b7ece4a23b60e62733cf6d6fc'

class State:
    def __init__(self):
        self.current = ST_STANDBY
        self.state_start_millis = None
        self.release_start_millis = None
        self.LED = 1

def send_message(message):
    print ("Sending message: {}".format(message))
    tree_id = get_tree_number()
    other_tree_id = tree_id ^ 1
    call(["curl", "http://" + BLYNK_SERVER + "/" + BLYNK_AUTH + "/update/V{0}?value={1}".format(other_tree_id, message)])

def get_state_handlers():
    state_handlers = {}
    state_handlers[ST_STANDBY] = in_standby
    state_handlers[ST_CHARGING] = in_charging
    state_handlers[ST_CHARGED] = in_charged
    state_handlers[ST_BEEN_INVITED] = in_been_invited
    state_handlers[ST_WIN] = in_win
    return state_handlers

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
        play_sound("my_01.wav")
    elif message == MSG_GOT_INVITED:
        to_state(state, ST_BEEN_INVITED, LED_BEEN_INVITED)
        play_sound("other_1.wav")

def in_charging(state, message):
    if message == MSG_RELEASE:
        to_state(state, ST_STANDBY, LED_STANDBY)
        pygame.mixer.music.stop()
    elif message == MSG_TICK:
        elapsed_time = millis() - state.state_start_millis
        if elapsed_time > CHARGE_TIME:
            to_state(state, ST_CHARGED, LED_CHARGED)
            play_sound("other_1.wav")
            send_message(MSG_GOT_INVITED)

    elif message == MSG_GOT_INVITED:
        to_state(state, ST_WIN, LED_WIN)
        play_sound("both_sound16.wav")

def in_charged(state, message):
    if message == MSG_RELEASE:
        state.release_start_millis = millis()
    elif message == MSG_GOT_WIN:
        to_state(state, ST_WIN, LED_WIN)
        play_sound("both_sound16.wav")
    elif message == MSG_GOT_INVITED:
        to_state(state, ST_WIN, LED_WIN)
        send_message(MSG_GOT_WIN)
        play_sound("both_sound16.wav")
    elif message == MSG_TICK:
        if state.release_start_millis:
            elapsed_time = millis() - state.release_start_millis
            print("elapsed time is {}\n".format(elapsed_time))
            if elapsed_time > CHARGE_RELEASE_TIME:
                to_state(state, ST_STANDBY, LED_STANDBY)
                pygame.mixer.music.stop()
                state.release_start_millis = None
                send_message(MSG_GOT_CHARGE_RELEASED)

def in_been_invited(state, message):
    if message == MSG_TOUCH:
        to_state(state, ST_WIN, LED_WIN)
        play_sound("both_sound16.wav")
        send_message(MSG_GOT_WIN)
    elif message == MSG_GOT_WIN:
        to_state(state, ST_WIN, LED_WIN)
        play_sound("both_sound16.wav")
    elif message == MSG_GOT_CHARGE_RELEASED:
        to_state(state, ST_STANDBY, LED_STANDBY)
        pygame.mixer.music.stop()

def in_win(state, message):
    if message == MSG_RELEASE or message == MSG_GOT_CHARGE_RELEASED:
        to_state(state, ST_STANDBY, LED_STANDBY)
        send_message(MSG_GOT_CHARGE_RELEASED)
        pygame.mixer.music.stop()

def state_machine(q):
    #last_state = state
    state = State()
    state_handlers = get_state_handlers()
    last_state = ST_STANDBY
    while True:
        global touchCount
        send_message(touchCount)
        time.sleep(0.5)
        #message =
        # .get()
        #if message != MSG_TICK:
        #    print("Got message: '" + message + "' while in state " + state.current + "\n")
        # run the method that handles the specific state we're in
        #state_handlers[state.current](state, message)
        if state.current != last_state:
            print("Now in state: {}\n".format(state.current))
            last_state = state.current

print('initializing blynk')
blynk = BlynkLib.Blynk(BLYNK_AUTH, server=BLYNK_SERVER)

@blynk.VIRTUAL_WRITE(0)
def v0_write_handler(value):
    global q
    if get_tree_number() == 0:
        global remoteTouchCount
        remoteTouchCount = int(value)
        print("V0 Got value: {}".format(value))

@blynk.VIRTUAL_WRITE(1)
def v1_write_handler(value):
    global q
    if get_tree_number() == 1:
        global remoteTouchCount
        remoteTouchCount = int(value)
        print("V1 Got value: {}".format(value))

def get_tree_number():
    return TREE_TO_TEST

def blynk_thread():
    while(True):
        try:
            blynk.run()
        except Exception as ex:
            print(ex)
            traceback.print_exc()
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)

tree_number = get_tree_number()
print("Tree number is: " + str(tree_number) + "\n");

q = Queue.Queue()

t = threading.Thread(target = state_machine, args = (q,))
t.daemon = True
t.start()

t = threading.Thread(target = blynk_thread)
t.daemon = True
t.start()


last_tick = millis()
last_touched = False
last_remoteTouchCount = 0
inWinningState = False

# Time to switch between touch and dont touch of the button
test_switch_time = 10
last_switch = millis() - test_switch_time
touched = False

while True:
    if millis() > last_switch + test_switch_time:
        touched = False#TODO not touched
        print('Button is {}'.format(touched))
        last_switch = millis()

    if touched:
      if last_touched == False:
        print('local charging started')
        pygame.mixer.music.stop()
        play_sound("my_01.wav")
        
      touchCount = touchCount + GROWING_SPEED
      if touchCount > PIXEL_COUNT:
        touchCount = PIXEL_COUNT
    else:
      if last_touched == True:
        print('local charging stopped')
        pygame.mixer.music.stop()


      if touchCount > 0 and touchCount <= SHRINKING_SPEED:
        print('local discharging ended')
        pygame.mixer.music.fadeout(2000)
        #pygame.mixer.music.load("")
        #pygame.mixer.music.play()

      touchCount = touchCount - SHRINKING_SPEED
      if touchCount <= 0:
        touchCount = 0

    time.sleep(0.05)
    
    # other end incoming sound handling:
    # give preference to local interaction over remote interaction
    if touchCount == 0:
      if last_remoteTouchCount == 0 and remoteTouchCount > 0:
        print('remote charging detected')
        pygame.mixer.music.stop()
        # We encode the other sound inside the remote number so for sound # 4 we send 4000
        # So if we light 50 leds it would be 4050
        if remoteTouchCount > 1000:
            other_sound = math.floor(remoteTouchCount / 1000)
            play_sound('other_{}.wav'.format(other_sound))
      else:
        if last_remoteTouchCount > remoteTouchCount:
          pygame.mixer.music.fadeout(2000)

    # handle winning state
    if remoteTouchCount > 0:
      if (remoteTouchCount == PIXEL_COUNT and touchCount == PIXEL_COUNT):
        if inWinningState == False:
          pygame.mixer.music.stop()
          play_sound("both_sound16.wav")
          inWinningState = True
      else:
        inWinningState = False


    if last_remoteTouchCount == PIXEL_COUNT and remoteTouchCount < PIXEL_COUNT:
      if touchCount == 0:
        pygame.mixer.music.fadeout(2000)
      else:
        pygame.mixer.music.stop()
        play_sound("my_01.wav")

    last_touched = touched
    last_remoteTouchCount = remoteTouchCount