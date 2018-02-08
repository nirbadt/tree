import socket
import sys
import os
import tree
import time
import argparse
import signal
from neopixel import *
import Adafruit_MPR121.MPR121 as MPR121


if (len(sys.argv) < 2):
	print "server.py <port>"
	exit(1)

sensor = tree.init_sensor()
strip = tree.init_strip()

###############################################################################3
## 
###############################################################################3
PORT = int(sys.argv[1])

print "now run:"
print "  server: ngrok tcp --region=eu --remote-addr=1.tcp.eu.ngrok.io:21351 " + str(PORT)
print "  client: python client.py 1.tcp.eu.ngrok.io 21351\n"

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('', PORT))
sock.listen(1)

print >>sys.stderr, 'starting up on %s port %s' % sock.getsockname()


while True:
    print >>sys.stderr, 'waiting for a connection'
    connection, client_address = sock.accept()
    try:
        print >>sys.stderr, 'client connected:', client_address
        connection.settimeout(0.1)

        tree.handle_loop(connection, sensor, strip);

    finally:
        connection.close()
