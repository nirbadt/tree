## Setup
Setup an internet network with name:Noden password:syntheos  /if it doesnot work try noden (no capital N)
Connect both units to electricty
Connect the USB coming out from the box, back into the Raspberry pie USB port (doesn't matter which one)
Connect the Raspberry pie to electricty through a standard micro usb B.
*As the Pie automatically runs the project code on startup, make sure you connect the Teenzy to the Pie before you connect the Pie to electricty. If not, the Pie's code will fail over miscommunication with the Teenzy.

	
## Test
Test it by sending a signal from one unit to the other. Please note, sending a signal takes time so it recoomeneded to connect at least 1 LED strip to each unit to see the signal moving.

## codes
You will need 3 codes - one for the RaspberryPie units (identical code for both units) and two for the Teenzy (one for each one of them).

## SSH
1) Check through routher what is the IP of the Pi
2) Login, user `pi`, password `raspberry`
4) ssh pi@192.168.1.104 (babypi)

## Libraries
For a new Rpi, install the MPR121 libraries: https://github.com/adafruit/Adafruit_Python_MPR121
and the 

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
https://drive.google.com/drive/u/0/folders/1VJmJFb3NY0qjUHO7iE7arsCX7nPm9Nrt

#### important commands
ssh pi@192.168.1.106 - Access Papa tree (Magenta)
ssh pi@192.168.1.107 - Access Baby tree (Cyan)
scp -r /Users/nirbadt/projects/tree/src/RaspberryPie pi@192.168.1.106:/home/pi/tree - copy files to Pi
git clone -b continuous-call https://github.com/nirbadt/tree.git / clones git repo specific branch
sudo reboot -h now
sudo shutdown -h now
sudo killall python /kill all running python scripts

