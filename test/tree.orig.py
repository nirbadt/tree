import os
import random
import socket
import time
import sys

def read_local_sensor():
	return int(random.getrandbits(8) & random.getrandbits(8) & 
		random.getrandbits(8) & random.getrandbits(8)) & 0xFF

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

def play_sound(local_sensor, remote_sensor):
	if (local_sensor & remote_sensor):
		print "SOUND"

def light_led(local_sensor, remote_sensor):
	if (local_sensor & remote_sensor):
		print "LED"

def handle_loop(connection):
	while True:
		local_sensor = read_local_sensor()
		print >>sys.stderr, 'local  sensor: %s' % hex(local_sensor)
		send_sensor_data_to_remote(connection, local_sensor)
		
		remote_sensor = read_remote_sensor(connection)
		print >>sys.stderr, 'remote sensor: %s' % hex(remote_sensor)

		play_sound(local_sensor, remote_sensor)
		light_led(local_sensor, remote_sensor)

		time.sleep(0.2)
