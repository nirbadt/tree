import sys
import time
import Adafruit_MPR121.MPR121 as MPR121
import serial
import pygame
import BlynkLib
import time
from subprocess import call

TREE_ID = 2
BLYNK_AUTH = '0417d2fac52a44518649ec5db2334f2d'

def millis():
    return int(round(time.time() * 1000))

# millisecs
WIN_DISENGAGE_DURATION = 2000
CHARGING_DURATION = 2000
INVITATION_ABORT_DURATION = 3000

SERIAL_PORT = '/dev/ttyACM0'

STATE_STANDBY = 10
STATE_CHARGING = 20
STATE_CHARGED = 30
STATE_INVITED = 40
STATE_WIN = 50

state = STATE_STANDBY
chargingStarted = -1
winDisengaged = -1
invitationAbortedTstamp = -1
initialized = False

print('initializing mpr121')
cap = MPR121.MPR121()
print('mpr121 initialized')

print('initializing serial')
ser = serial.Serial(SERIAL_PORT)
ser.baudrate = 9600
print('serial initialized')

# Initialize Sound
print('initializing sound')
pygame.mixer.init()
print('sound initialized')

ser.write('1')
pygame.mixer.music.load("sounds/match1.wav")
pygame.mixer.music.play()

if not cap.begin(busnum=1):
    print('Error initializing MPR121.  Check your wiring!')
    sys.exit(1)
else:
    print('cap initialized')

# Initialize Blynk
print('initializing blynk')
blynk = BlynkLib.Blynk(BLYNK_AUTH)
print('blynk initialized')


#def my_user_task():
#    # do any non-blocking operations
#    print('Action')
#    blynk.virtual_write(TREE_ID, time.ticks_ms() // 1000)

#blynk.set_user_task(my_user_task, 3000)

print('starting...')
call(["curl", "http://blynk-cloud.com/0417d2fac52a44518649ec5db2334f2d/update/V1?value=10"])

def game_task():
    global state
    global chargingStarted
    global winDisengaged
    global initialized
    global invitationAbortedTstamp
    
    if(True):
        if initialized == False:
            print('initializing state to standby')
#            blynk.virtual_write(TREE_ID, STATE_STANDBY)
#            ser.write('1')
            state = STATE_STANDBY
            initialized = True
            
        if state == STATE_STANDBY:
            if cap.is_touched(0):
                pygame.mixer.music.load("sounds/match2.wav")
                pygame.mixer.music.play()
                ser.write('2')
#                blynk.virtual_write(TREE_ID, STATE_CHARGING)
                chargingStarted = millis()
                state = STATE_CHARGING

        elif state == STATE_CHARGING:
            if not cap.is_touched(0):
                pygame.mixer.music.load("sounds/match1.wav")
                pygame.mixer.music.play()
                ser.write('1')
#                blynk.virtual_write(TREE_ID, STATE_STANDBY)
                state = STATE_STANDBY
                print('state = STATE_STANDBY')
                chargingStarted = -1
                
            elif(millis() - chargingStarted) > CHARGING_DURATION:
                pygame.mixer.music.load("sounds/match3.wav")
                pygame.mixer.music.play()
                ser.write('3')
#                blynk.virtual_write(TREE_ID, STATE_CHARGED)
                invitationAbortedTstamp = -1
                state = STATE_CHARGED

        elif state == STATE_CHARGED:
            if not cap.is_touched(0):
                if invitationAbortedTstamp < 0:
                    invitationAbortedTstamp = millis()
                elif (millis() - invitationAbortedTstamp) > INVITATION_ABORT_DURATION:
                    pygame.mixer.music.load("sounds/match1.wav")
                    pygame.mixer.music.play()
#                    blynk.virtual_write(TREE_ID, STATE_STANDBY)
                    ser.write('1')
                    print('state = STATE_STANDBY')
                    state = STATE_STANDBY
            else:
                invitationAbortedTstamp = -1

        elif state == STATE_INVITED:
            if cap.is_touched(0):
                pygame.mixer.music.load("sounds/match5.wav")
                pygame.mixer.music.play()
                ser.write('5')
                winDisengaged = millis()
                state = STATE_WIN
                winDisengaged = millis()
#                blynk.virtual_write(TREE_ID, STATE_WIN)
            

        elif state == STATE_WIN:
            if cap.is_touched(0):
                winDisengaged = millis()
                
            elif (millis() - winDisengaged) > WIN_DISENGAGE_DURATION:
                pygame.mixer.music.load("sounds/match1.wav")
                pygame.mixer.music.play()
#                blynk.virtual_write(TREE_ID, STATE_STANDBY)
                ser.write('1')
                print('state = STATE_STANDBY')
                state = STATE_STANDBY
                                
            print('winwinwin')
        time.sleep(0.2)
#        blynk.virtual_write(TREE_ID, state)

# blynk.set_user_task(game_task, 500)

# Register virtual pin handler
@blynk.VIRTUAL_WRITE(1)
def v1_write_handler(value):
    global state
    print('got: ')
    print(value)
    other_tree_state = int(value)
    print('state:')
    print(state)
    if not state == STATE_WIN:
        print('test 0')
        if other_tree_state == STATE_STANDBY or other_tree_state == STATE_CHARGING:
            if state == STATE_INVITED:
                pygame.mixer.music.load("sounds/match1.wav")
                pygame.mixer.music.play()
                state = STATE_STANDBY
                ser.write('1')
                blynk.virtual_write(TREE_ID, STATE_STANDBY)

        elif other_tree_state == STATE_CHARGED:
            if not state == STATE_INVITED:
                pygame.mixer.music.load("sounds/match4.wav")
                pygame.mixer.music.play()
                state = STATE_INVITED
                ser.write('4')
                blynk.virtual_write(TREE_ID, STATE_INVITED)

        elif other_tree_state == STATE_WIN:
            if (not state == STATE_WIN) and (not state == STATE_STANDBY):
                pygame.mixer.music.load("sounds/match5.wav")
                pygame.mixer.music.play()
                state = STATE_WIN
                ser.write('5')
                winDisengaged = millis()                
                blynk.virtual_write(TREE_ID, STATE_WIN)
    else:
        print('test 1')
        if not other_tree_state == STATE_WIN:
            print('falling out of grace')
            pygame.mixer.music.load("sounds/match1.wav")
            pygame.mixer.music.play()
            state = STATE_STANDBY
            ser.write('1')
            blynk.virtual_write(TREE_ID, STATE_STANDBY)

    game_task()

    call(["curl", "http://blynk-cloud.com/0417d2fac52a44518649ec5db2334f2d/update/V{0}?value={1}".format(TREE_ID, state)])


while(True):
    try:
        blynk.run()
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print (message)
    
# write pin value:
# http://blynk-cloud.com/0417d2fac52a44518649ec5db2334f2d/update/V1?value=10

# get pin value:
# http://blynk-cloud.com/0417d2fac52a44518649ec5db2334f2d/get/pin/V2
