#!/usr/bin/python

import time
import threading
import irclib
import wiringpi

LED_PIN = 3

wiringpi.wiringPiSetupSys() # for unprivileged access to GPIO pins
wiringpi.pinMode(LED_PIN, 1) # output


def flash_LED(count=5, ontime=100, offtime=200):
	"""Flash the LED count times, one for ontime ms, off for offtime ms"""
	for i in xrange(count):
		wiringpi.digitalWrite(LED_PIN, 1)
		time.sleep(ontime/1000.)
		wiringpi.digitalWrite(LED_PIN, 0)
		time.sleep(offtime/1000.)


def on_pubmsg(c, e):
	if [i for i in e.arguments()[0] if i in bot.users.keys()]:
		th = threading.Timer(0, flash_LED)
		th.start()

def on_action(c, e):
	if [i for i in e.arguments()[0] if i in bot.users.keys()]:
		th = threading.Timer(0, flash_LED)
		th.start()


botmodulename = "gpio_flash"
hooks = {
	"pubmsg" : on_pubmsg,
	"action" : on_action
	}
bot = None #this will be set by the bot that loads the module

