import socket
import sys
import fcntl, os
import errno
import time
import tree
import os


print "client.py <address> <port>\n"

connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (sys.argv[1], int(sys.argv[2]))

print >>sys.stderr, 'connecting to %s port %s' % server_address
connection.connect(server_address)
connection.settimeout(0.1)

sensor = tree.init_sensor()
strip = tree.init_strip()

tree.handle_loop(connection, sensor, strip);

connection.close()
