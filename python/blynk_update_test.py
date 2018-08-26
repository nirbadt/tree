import BlynkLib
import time

BLYNK_AUTH = '0417d2fac52a44518649ec5db2334f2d'

# Initialize Blynk
blynk = BlynkLib.Blynk(BLYNK_AUTH)

@blynk.VIRTUAL_WRITE(1)
def v1_write_handler(value):
    print('got: ')
    print(value)
#    if value == STATE_CHARGED:
#        state = STATE_INVITED
#    if value == STATE_WIN:
#        state = STATE_WIN

# Start Blynk (this call should never return)
blynk.run()
