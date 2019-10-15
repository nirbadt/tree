import Queue
import threading
import time
import BlynkLib
import Adafruit_MPR121.MPR121 as MPR121
import subprocess
import serial
import pygame

from subprocess import call


PIXEL_COUNT = 600
GROWING_SPEED = 3
SHRINKING_SPEED = 6

CHARGE_RELEASE_TIME = 0.5
CHARGE_TIME = 7

SERIAL_PORT = '/dev/ttyACM0'

BLYNK_AUTH = 'ac4b8c5b7ece4a23b60e62733cf6d6fc'

host_name = str(subprocess.check_output(['hostname']))
TREE_ID_LOCAL = 0 if 'papa' in host_name else 1
TREE_ID_REMOTE = TREE_ID_LOCAL ^ 1

REAL_LEN = PIXEL_COUNT // 2

px_local = 0
px_remote = 0
px_remote_prev = 0

touch_state = False
touch_state_prev = False
RAINBOW = False

try: 
    print('initializing..')
    ser = serial.Serial(SERIAL_PORT)
    ser.baudrate = 115200
    pygame.mixer.init()
    pygame.mixer.music.play(-1)
    cap = MPR121.MPR121()
    cap.begin(busnum=1)
    blynk = BlynkLib.Blynk(BLYNK_AUTH, server='139.59.206.133')
except IOError as e:
    print("Hardware init failure")
    print(e)
    exit
    

print("Initialized. Tree number is:", TREE_ID_LOCAL)

def music_play(track):
    pygame.mixer.music.stop()
    pygame.mixer.music.load("/home/pi/tree/sounds/" + track + ".wav")
    pygame.mixer.music.play()


def music_stop():
    pygame.mixer.music.fadeout(2000)

print("starting blynk functions")

@blynk.VIRTUAL_WRITE(0)
def v0_write_handler(value):
    if TREE_ID_LOCAL == 0:
        global px_remote
        px_remote = int(value)


@blynk.VIRTUAL_WRITE(1)
def v1_write_handler(value):
    if TREE_ID_LOCAL == 1:
        global px_remote
        px_remote = int(value)


print("blynk functions started")
def publish_touch_count():
    while True:
        try:
            call(["curl", "http://139.59.206.133/" + BLYNK_AUTH +
                  "/update/V{0}?value={1}".format(TREE_ID_REMOTE, px_local)])
        except Exception as ex:
            print(ex)

        time.sleep(0.5)


def blynk_thread():
    while(True):
        try:
            blynk.run()
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)

def read_touch_state():
    global touch_state
    while True:
        temp_touch_state = cap.is_touched(0)
        
        if temp_touch_state != touch_state_prev:
            time.sleep(0.5)
            
            if temp_touch_state == cap.is_touched(0):
                #state is not changed in last 0.5s, so it counts
                touch_state = temp_touch_state
            
        time.sleep(0.1)
    
def ping_JBL():
    while True:
        time.sleep(300)
        if pygame.mixer.music.get_busy() == False:
            music_play("keep_alive_sound")
            time.sleep(1)
            music_stop()
            
print("starting threads")
t1 = threading.Thread (target=publish_touch_count)
t1.daemon = True
t1.start()

t2 = threading.Thread(target=blynk_thread)
t2.daemon = True
t2.start()

t3 = threading.Thread(target=read_touch_state)
t3.daemon = True
t3.start()

jbl = threading.Thread(target=ping_JBL)
jbl.daemon = True
jbl.start()

music_play("match1")

print("starting main loop")

while True:
    time.sleep(0.05)


    if touch_state:
        if touch_state_prev == False:  # print 'local charging started'
            music_play("my_sound16")

        px_local = px_local + GROWING_SPEED
        if px_local > PIXEL_COUNT:
            px_local = PIXEL_COUNT
    else:
        if touch_state_prev == True:  # print 'local charging stopped'
            music_play("my_sound16_reversed2")

        if px_local > 0 and px_local <= SHRINKING_SPEED:  # print 'local discharging ended'
            music_stop()

        px_local = px_local - SHRINKING_SPEED
        if px_local < 0:
            px_local = 0
            
            
    

    # incoming call
    if px_remote_prev <= REAL_LEN and px_remote > REAL_LEN:  # print 'remote charging detected'
        music_play("other_sound16")
    else:
        if px_remote_prev > px_remote and px_local == 0:
            music_stop()

    #RAINBOW
    if (px_remote == px_local == PIXEL_COUNT):
        if not RAINBOW:
            music_play("both_sound16")
            RAINBOW = True
    else:
        RAINBOW = False

    if px_remote_prev == PIXEL_COUNT and px_remote < PIXEL_COUNT:
        if px_local == 0 or px_local == PIXEL_COUNT:
            music_stop()
        elif pygame.mixer.music.get_busy == False:
            music_play("my_sound16")

    touch_state_prev = touch_state
    px_remote_prev = px_remote

    leds_px_local = px_local
    if px_local == PIXEL_COUNT:
        leds_px_local = REAL_LEN
    elif px_local >= REAL_LEN:
        leds_px_local = REAL_LEN - 1

    leds_px_remote = 0 if px_remote < REAL_LEN else px_remote - REAL_LEN

    try:
        ser.write("{} {}".format(leds_px_local, leds_px_remote))
    except IOError as e:
        print("teensy is unavailable.")
        print(e)
        
    # print("Real values:       {} {}".format(px_local, px_remote))
    # print("Sending to teensy: {} {}".format(leds_px_local, leds_px_remote))