
# First time init on the pi
1. Install ngrock by downloading it from here:
`https://ngrok.com/download`
2. Sign up for ngrock
3. Connect your auth token (REPLACE WITH YOURS)
`./ngrok authtoken 24AUTH_TOKEN_REPLACE_ME`
4. pip3 install -r requirements.txt

# Testing
To test connect one hand
Then run
1.cd src
2.pip3 install -r requirements.txt
3.python3 test.py 

## System architecture
We have 2 raspberry pie. One is called `Papa` (The server) and 
the other is called `Baby` (The client that connect to the server)

## TODO
	* make it locally testable
	* client/server unification and agnostic auto-discovery
	 

## Startup
### Papa - server
```
# Terminal 1
ssh pi@PAPA-IP
ngrok tcp --region=eu --remote-addr=1.tcp.eu.ngrok.io:21351 10000

# Trerminal 2
ssh pi@PAPA-IP
cd Tree
sudo python server.py 10000
```

### Baby - client
```
ssh pi@BABY-IP
cd Tree
sudo python client.py 1.tcp.eu.ngrok.io 21351
```

## Setup the pi
1) Install the os when prompted
2) Preferences -> Enable SSH
3) Login, user `pi`, password `raspberry`
3.5) Make sure you set the hostname of one of them to be `papatree` 
4) ssh pi@192.168.1.104 (babypi)
5) soft
```bash
	sudo apt-get update 
	sudo apt-get install p7zip-full 
	sudo apt-get install apache2 -y 
	sudo apt-get install -y git 
	sudo apt-get install python-twisted 
	sudo apt-get install socat 
```
6) Libraries
	
7) download and install ngrok
	* linux, arm -> wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-arm.zip
	* unzip ngrok-stable-linux-arm.zip
	* sudo mv ./ngrok /usr/local/bin/
	* ngrok authtoken TOKEN
	* ngrok http 80
	* ngrok tcp 20 -> ssh pi@0.tcp.ngrok.io -oPort=16865
	* ngrok tcp --region=eu --remote-addr=1.tcp.eu.ngrok.io:21351 10000
	* ngrok tcp --region=eu --remote-addr=1.tcp.eu.ngrok.io:21352 10000

8) Capasitive
	* connect a banaba
	* run ~/Adafruit_Python_MPR121/examples $ sudo python simpletest.py
	* touch banana

## Capacitive Touch MPR121
Seems like what we need, 12 inputs, threshold can be set.
https://www.adafruit.com/product/2340
Code here:
https://learn.adafruit.com/mpr121-capacitive-touch-sensor-on-raspberry-pi-and-beaglebone-black
https://github.com/adafruit/Adafruit_Python_MPR121


## Repos
https://github.com/Yahavw/shula
https://github.com/Yahavw/shula/blob/master/rpi/rpi_config.json

## Disable soundcard
```
sudo vi /etc/modprobe.d/alsa-blacklist.conf
blacklist snd_bcm2835
```

## Resources
http://www.giantflyingsaucer.com/blog/?p=4967
http://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/patterns/pubsub.html

http://www.brynosaurus.com/pub/net/p2pnat/


## Log
### 8/2/2018
pi@babypi:~/Tree $ sudo python server-pi.py 10001
pi@babypi:~/Tree $ ngrok tcp --region=eu --remote-addr=1.tcp.eu.ngrok.io:21351 10001
pi@papapi:~/Tree $ sudo python client.py 1.tcp.eu.ngrok.io 21351

### 5/3/2018

## 29/7/2018
### Tree states
https://docs.google.com/spreadsheets/d/175IhOrYseiRWdDT4lwTgxA61GhVt3Ul3eON0_b8md2s/edit#gid=0

### Definiton document
https://docs.google.com/document/d/1GKJMDmAp9SjPEdWVMSUOmdqRxPe0D4RtXTn6_ycK0vU/edit#

# FAQ
How to upload directly from my computer to the pi?
```
scp -r ~/Documents/projects/tree/src/ pi@10.0.0.6:/home/pi/tree/python
```
