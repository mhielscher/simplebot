#!/usr/bin/python

import threading
import random

def do_bork(c, s, t, ch, a):
	random.seed()
	c.privmsg(t, "BORK BORK BORK")
	"""
	tm = 0
	for i in range(random.randrange(0, 6)):
		msg = "BORK "*random.randrange(1,5)
		timer = threading.Timer(random.randrange(1,16), c.privmsg, [t, msg])
		timer.start()
	"""

botmodulename = "bork"
commands = {
	"bork" : (do_bork, 0)
	}
help = {
	"bork" : ("BORK!", "bork", "BORKs a random number of times.")
	}
bot = None #this will be set by the bot that loads the module
