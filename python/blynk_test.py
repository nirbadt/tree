import BlynkLib
import time

BLYNK_AUTH = '0417d2fac52a44518649ec5db2334f2d'

# Initialize Blynk
blynk = BlynkLib.Blynk(BLYNK_AUTH)

# Register Virtual Pins
@blynk.VIRTUAL_WRITE(1)
def my_write_handler(value):
    print('Current V1 value: {}'.format(value))

@blynk.VIRTUAL_READ(2)
def my_read_handler():
    # this widget will show some time in seconds..
    blynk.virtual_write(2, time.ticks_ms() // 1000)


# Start Blynk (this call should never return)
blynk.run()
