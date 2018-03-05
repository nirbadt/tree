import os
import random
import socket
import time
import sys
import argparse
import signal
from neopixel import *
import Adafruit_MPR121.MPR121 as MPR121


def init_sensor():
	sensor = MPR121.MPR121()
	if not sensor.begin():
	    print('Error initializing MPR121.  Check your wiring!')
	    sys.exit(1)
	return sensor

def init_strip():
	# LED strip configuration:
	LED_COUNT      = 20      # Number of LED pixels.
	LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
	#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
	LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
	LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
	LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
	LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
	LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
	LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour order

	strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
	# Intialize the library (must be called once before other functions).
	strip.begin()
	return strip


def read_local_sensor(cap):
	current_touched = int(cap.touched() & 0xFF)
	return current_touched

def read_remote_sensor(connection):
	remote_sensor = 0
	try:
		remote_sensor = connection.recv(1)
	except socket.timeout, e:
		err = e.args[0]
		if err == 'timed out':
			time.sleep(0.1)
			print 'recv timed out, retry later'
			return 0
		else:
			print e
			return 0
	except socket.error, e:
		print e
		return 0
	else:
		if len(remote_sensor) == 0:
			print 'orderly shutdown on server end'
			return 0
		else:
			# got a message do something
			remote_sensor = ord(remote_sensor[0])
	return remote_sensor

def send_sensor_data_to_remote(connection, data):
	try:
		connection.sendall(chr(data))
	except socket.error, e:
		print e
		return 1
	return 0

def sensor_bar(sensor_data, index):
	return (sensor_data >> index) & 0x1


def handle_loop(connection, sensor, strip):
	last_local_sensor = read_local_sensor(sensor)
	last_remote_sensor = 0

	while True:

		for j in range(1, 8):

			current_local_sensor = read_local_sensor(sensor)
			print >>sys.stderr, 'local  sensor: %s' % hex(current_local_sensor)
			
			send_sensor_data_to_remote(connection, current_local_sensor)
			
			current_remote_sensor = read_remote_sensor(connection)
			print >>sys.stderr, 'remote sensor: %s' % hex(current_remote_sensor)

			############################################

			print "PLAY: %d %d %d %d" % (last_local_sensor, current_local_sensor, last_remote_sensor, current_remote_sensor)
			for i in range(5):
				pin_bit = 1 << i
				local_touched = current_local_sensor & pin_bit and not last_local_sensor & pin_bit
				local_released = not current_local_sensor & pin_bit and last_local_sensor & pin_bit;
				remote_touched = current_remote_sensor & pin_bit and not last_remote_sensor & pin_bit
				remote_released = not current_remote_sensor & pin_bit and last_remote_sensor & pin_bit;

				if local_touched or remote_touched:
					print('{0} touched!'.format(i))
					strip.setPixelColor(0,Color(0,0,255))
				
				elif local_released or remote_released:
					print('{0} released!'.format(i))
					strip.setPixelColor(0,Color(0,0,0))

				Energy = strip.getPixelColor(j-1)
				strip.setPixelColor(j, Energy)
				strip.show()

				time.sleep(0.005)

			last_local_sensor = current_local_sensor
			last_remote_sensor = current_remote_sensor
