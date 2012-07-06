#!/usr/bin/python

import random
import time

def do_hug(c, s, t, ch, a):
	if len(a) < 1:
		nicks = ["me"]
	elif (' '.join(a)).lower() == "everyone individually".lower() or (' '.join(a)).lower() == "everybody individually".lower():
		nicks = bot.channels[ch].users()
	else:
		nicks = a
	for n in nicks:
		verb = random.choice(["hugs", "cuddles", "squishes", "bear hugs", "squeezes", "snuggles with"])
		if n.lower() == "me".lower():
			c.action(ch, "%s %s." % (verb, s))
		elif n.lower() == "everybody".lower() or n.lower() == "everyone".lower() or n.lower() == "all".lower():
			c.action(ch, "%s everyone." % (verb))
		else:
			c.action(ch, "%s %s." % (verb, n))
		time.sleep(random.normalvariate(.667, .33))

botmodulename = "hug"
commands = {
	"hug" : (do_hug, 0)
	}
help = {
	"hug" : ("Hugs you, or whoever you tell it to.", "hug [channel] [me|everyone|<nick>]", "Hugs you, or everyone, or <nick>.")
	}
bot = None #this will be set by the bot that loads the module
