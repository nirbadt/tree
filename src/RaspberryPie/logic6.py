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
TREE_ID = 0 if 'papa' in host_name else 1
OTHER_TREE_ID = TREE_ID ^ 1


touchCount = 0
remoteTouchCount = 0

last_touched = False
last_remoteTouchCount = 0
inWinningState = False

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


print("Initialized. Tree number is: " + str(TREE_ID) + "\n")

@blynk.VIRTUAL_WRITE(0)
def v0_write_handler(value):
    if TREE_ID == 0:
        global remoteTouchCount
        remoteTouchCount = int(value)
        #print("V0 Got value: " + remoteTouchCount + "\n")


@blynk.VIRTUAL_WRITE(1)
def v1_write_handler(value):
    if TREE_ID == 1:
        global remoteTouchCount
        remoteTouchCount = int(value)
        #print("V1 Got value: " + remoteTouchCount + "\n")


def publish_touch_count():
    while True:
        # global touchCount
        call(["curl", "http://139.59.206.133/" + BLYNK_AUTH +
              "/update/V{0}?value={1}".format(OTHER_TREE_ID, touchCount)])

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

    touched = cap.is_touched(0)

    if touched:
        if last_touched == False:  # print 'local charging started'
            music_play("my_sound16")

        touchCount = touchCount + GROWING_SPEED
        if touchCount > PIXEL_COUNT:
            touchCount = PIXEL_COUNT
    else:
        if last_touched == True:  # print 'local charging stopped'
            music_play("my_sound16_reversed2")

        if touchCount > 0 and touchCount <= SHRINKING_SPEED:  # print 'local discharging ended'
            music_stop()

        touchCount = touchCount - SHRINKING_SPEED
        if touchCount <= 0:
            touchCount = 0

    # other end incoming sound handling:
    # give preference to local interaction over remote interaction
    if touchCount == 0:

        if last_remoteTouchCount == 0 and remoteTouchCount > 0:  # print 'remote charging detected'
            music_play("other_sound16")
        else:
            if last_remoteTouchCount > remoteTouchCount:
                music_stop()

    # handle winning state
    if (remoteTouchCount == PIXEL_COUNT and touchCount == PIXEL_COUNT):
        if inWinningState == False:
            music_play("both_sound16")
            inWinningState = True
    else:
        inWinningState = False

    if last_remoteTouchCount == PIXEL_COUNT and remoteTouchCount < PIXEL_COUNT:
        if touchCount == 0:
            music_stop()
        else:
            music_play("my_sound16")

    last_touched = touched
    last_remoteTouchCount = remoteTouchCount

    local_touch = touchCount
    if touchCount == PIXEL_COUNT:
        local_touch = REAL_LEN
    elif touchCount >= REAL_LEN:
        local_touch = REAL_LEN - 1

    remote_touch = 0 if remoteTouchCount < REAL_LEN else remoteTouchCount - REAL_LEN

    ser.write("{} {}".format(local_touch, remote_touch))
