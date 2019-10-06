import Queue
import threading
import time
import BlynkLib
import Adafruit_MPR121.MPR121 as MPR121
import subprocess
import serial
import pygame

from subprocess import call


PIXEL_COUNT = 480
REAL_LEN = PIXEL_COUNT // 2
GROWING_SPEED = 6
SHRINKING_SPEED = 6

CHARGE_RELEASE_TIME = 0.5
CHARGE_TIME = 7

SERIAL_PORT = '/dev/ttyACM0'

BLYNK_AUTH = 'ac4b8c5b7ece4a23b60e62733cf6d6fc'

host_name = str(subprocess.check_output(['hostname']))
TREE_ID_LOCAL = 0 if 'papa' in host_name else 1
TREE_ID_REMOTE = TREE_ID_LOCAL ^ 1


px_local = 0
px_remote = 0

touch_state_prev = False
px_remote_prev = 0
RAINBOW = False

print('initializing')
ser = serial.Serial(SERIAL_PORT)
ser.baudrate = 115200
pygame.mixer.init()

pygame.mixer.music.load("match1.wav")
pygame.mixer.music.play()

cap = MPR121.MPR121()
if not cap.begin(busnum=1):
    print('Error initializing MPR121.')
    sys.exit(1)

blynk = BlynkLib.Blynk(BLYNK_AUTH, server='139.59.206.133')


print("Initialized. Tree number is: " + str(TREE_ID_LOCAL) + "\n")

@blynk.VIRTUAL_WRITE(0)
def v0_write_handler(value):
    if TREE_ID_LOCAL == 0:
        global px_remote
        px_remote = int(value)
        #print("V0 Got value: " + px_remote + "\n")


@blynk.VIRTUAL_WRITE(1)
def v1_write_handler(value):
    if TREE_ID_LOCAL == 1:
        global px_remote
        px_remote = int(value)
        #print("V1 Got value: " + px_remote + "\n")


def publish_touch_count():
    while True:
        try:
            call(["curl", "http://139.59.206.133/" + BLYNK_AUTH +  "/update/V{0}?value={1}".format(TREE_ID_REMOTE, px_local)])
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


t1 = threading.Thread(target=publish_touch_count)
t1.daemon = True
t1.start()

t2 = threading.Thread(target=blynk_thread)
t2.daemon = True
t2.start()


def music_play(track):
    pygame.mixer.music.stop()
    pygame.mixer.music.load("/home/pi/tree/sounds/" + track + ".wav")
    pygame.mixer.music.play()


def music_stop():
    pygame.mixer.music.fadeout(2000)
    
    
try:
  print(blynk.log)
except:
    print("blynk.log is not printable")



while True:
    time.sleep(0.05)

    touch_state = cap.is_touched(0)

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

    # other end incoming sound handling:
    # give preference to local interaction over remote interaction
    if px_local == 0:
        if px_remote_prev == 0 and px_remote > 0:  # print 'remote charging detected'
            music_play("other_sound16")
        else:
            if px_remote_prev > px_remote:
                music_stop()

    # handle winning state
    if (px_remote == PIXEL_COUNT and px_local == PIXEL_COUNT):
        if RAINBOW == False:
            music_play("both_sound16")
            RAINBOW = True
    else:
        RAINBOW = False

    if px_remote_prev == PIXEL_COUNT and px_remote < PIXEL_COUNT:
        if px_local == 0:
            music_stop()
        else:
            music_play("my_sound16")

    touch_state_prev = touch_state
    px_remote_prev = px_remote

    leds_px_local = px_local
    if px_local == PIXEL_COUNT:
        leds_px_local = REAL_LEN
    elif px_local >= REAL_LEN:
        leds_px_local = REAL_LEN - 1

    leds_px_remote = 0 if px_remote < REAL_LEN else px_remote - REAL_LEN

    ser.write("{} {}".format(leds_px_local, leds_px_remote))
    print("Real values:       {} {}".format(px_local, px_remote))
    print("Sending to teensy: {} {}".format(leds_px_local, leds_px_remote))
