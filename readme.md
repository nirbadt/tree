### TODO
	Done
		[x] client<->server communication
		[x] sensing improvements

	D
		[ ] Cleanup and commit to git
		[ ] make it locally testable
		[ ] client/server python cleanup
		[ ] client/server agnostic auto-discovery
	N
		[ ] Play implementation
	Integration
		[ ] Activate strip code
		[ ] 

## Setup
1) Install the os when prompted
2) Preferences -> Enable SSH
3) Login, user `pi`, password `raspberry`
4) ssh pi@192.168.1.104 (babypi)
5) soft
	sudo apt-get update
	sudo apt-get install p7zip-full
	sudo apt-get install apache2 -y
	sudo apt-get install -y git
	sudo apt-get install python-twisted
	sudo apt-get install socat
6) Libraries
	
6) download and install ngrok
	a) linux, arm -> wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-arm.zip
	b) unzip ngrok-stable-linux-arm.zip
	c) sudo mv ./ngrok /usr/local/bin/
	d) ngrok authtoken TOKEN
	e) ngrok http 80
	f) ngrok tcp 20 -> ssh pi@0.tcp.ngrok.io -oPort=16865
		ngrok tcp --region=eu --remote-addr=1.tcp.eu.ngrok.io:21351 10000
		ngrok tcp --region=eu --remote-addr=1.tcp.eu.ngrok.io:21352 10000
7) Capasitive
	a) connect a banaba
	b) run ~/Adafruit_Python_MPR121/examples $ sudo python simpletest.py
	c) touch banana

## Capacitive Touch MPR121
Seems like what we need, 12 inputs, threshold can be set.
https://www.adafruit.com/product/2340
Code here:
https://learn.adafruit.com/mpr121-capacitive-touch-sensor-on-raspberry-pi-and-beaglebone-black
https://github.com/adafruit/Adafruit_Python_MPR121



## Repos
https://github.com/Yahavw/shula
https://github.com/Yahavw/shula/blob/master/rpi/rpi_config.json


http://www.giantflyingsaucer.com/blog/?p=4967
http://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/patterns/pubsub.html

http://www.brynosaurus.com/pub/net/p2pnat/


### 8/2/2018
pi@babypi:~/Tree $ sudo python server-pi.py 10001
pi@babypi:~/Tree $ ngrok tcp --region=eu --remote-addr=1.tcp.eu.ngrok.io:21351 10001

pi@papapi:~/Tree $ sudo python client.py 1.tcp.eu.ngrok.io 21351
