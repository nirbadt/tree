import Queue
import threading
import time
import BlynkLib
import Adafruit_MPR121.MPR121 as MPR121
import subprocess
import serial
import pygame

from subprocess import call

SERIAL_PORT = '/dev/ttyACM0'
#SERIAL_PORT = '/dev/ttyACM0'

print('initializing serial')
ser = serial.Serial(SERIAL_PORT)
ser.baudrate = 9600
print('serial initialized')

#pygame.mixer.pre_init(44100, 16, 2, 4096) #frequency, size, channels, buffersize
#pygame.init() #turn all of pygame on.

touchCount = 0
remoteTouchCount1 = 0

print('initializing sound')
pygame.mixer.init()
print('sound initialized')

pygame.mixer.music.load("sounds/match1.wav")
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
    call(["curl", "http://139.59.206.133/" + BLYNK_AUTH + "/update/V{0}?value={1}".format(other_tree_id, message)])

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
    ser.write(LED_state)
    state.release_start_millis = None
    state.state_start_millis = millis()

def in_standby(state, message):
    if message == MSG_TOUCH:
        to_state(state, ST_CHARGING, LED_CHARGING)
        pygame.mixer.music.load("my_sound16.wav")
        pygame.mixer.music.play()
    elif message == MSG_GOT_INVITED:
        to_state(state, ST_BEEN_INVITED, LED_BEEN_INVITED)
        pygame.mixer.music.load("other_sound16.wav")
        pygame.mixer.music.play()
def in_charging(state, message):
    if message == MSG_RELEASE:
        to_state(state, ST_STANDBY, LED_STANDBY)
        pygame.mixer.music.stop()
    elif message == MSG_TICK:
        elapsed_time = millis() - state.state_start_millis
        if elapsed_time > CHARGE_TIME:
            to_state(state, ST_CHARGED, LED_CHARGED)
            pygame.mixer.music.load("other_sound16.wav")
            pygame.mixer.music.play()
            send_message(MSG_GOT_INVITED)

    elif message == MSG_GOT_INVITED:
        to_state(state, ST_WIN, LED_WIN)
        pygame.mixer.music.load("both_sound16.wav")
        pygame.mixer.music.play()

def in_charged(state, message):
    if message == MSG_RELEASE:
        state.release_start_millis = millis()
    elif message == MSG_GOT_WIN:
        to_state(state, ST_WIN, LED_WIN)
        pygame.mixer.music.load("both_sound16.wav")
        pygame.mixer.music.play()
    elif message == MSG_GOT_INVITED:
        to_state(state, ST_WIN, LED_WIN)
        send_message(MSG_GOT_WIN)
        pygame.mixer.music.load("both_sound16.wav")
        pygame.mixer.music.play()
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
        pygame.mixer.music.load("both_sound16.wav")
        pygame.mixer.music.play()
        send_message(MSG_GOT_WIN)
    elif message == MSG_GOT_WIN:
        to_state(state, ST_WIN, LED_WIN)
        pygame.mixer.music.load("both_sound16.wav")
        pygame.mixer.music.play()
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
        #message = q.get()
        #if message != MSG_TICK:
        #    print("Got message: '" + message + "' while in state " + state.current + "\n")
        # run the method that handles the specific state we're in
        #state_handlers[state.current](state, message)
        if state.current != last_state:
            print("Now in state: " + state.current + "\n")
            last_state = state.current

print('initializing blynk')
blynk = BlynkLib.Blynk(BLYNK_AUTH, server='139.59.206.133')

@blynk.VIRTUAL_WRITE(0)
def v0_write_handler(value):
    global q
    if get_tree_number() == 0:
        #q.put(value)
        global remoteTouchCount1
        remoteTouchCount1 = value
        print("V0 Got value: " + remoteTouchCount1 + "\n")

@blynk.VIRTUAL_WRITE(1)
def v1_write_handler(value):
    global q
    if get_tree_number() == 1:
        #q.put(value)
        global remoteTouchCount1
        remoteTouchCount1 = value
        print("V1 Got value: " + remoteTouchCount1 + "\n")

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

None
#previous_touched = False


last_tick = millis()
while True:
    touched = cap.is_touched(0)
    if touched:
      touchCount = touchCount + 1
      if touchCount > 240:
        touchCount = 240
    else:
      touchCount = touchCount - 3
      if touchCount < 0:
        touchCount = 0
    #send_message(touchCount)
    ser.write("{} {}".format(touchCount, remoteTouchCount1))
    time.sleep(0.1)
    print("{} {}".format(touchCount, remoteTouchCount1))
    elapsed_time = millis() - last_tick
    if elapsed_time > TICK_TIME:
        last_tick = millis()
#        q.put(MSG_TICK)
#    previous_touched = touched
