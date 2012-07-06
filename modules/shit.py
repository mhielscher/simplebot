#!/usr/bin/python

def do_shit(c, s, t, ch, a):
	c.privmsg(t, "Shit indeed!")

botmodulename = "shit"
commands = {
	"shit" : (do_shit, 0)
	}
help = {
	"shit" : ("Shit indeed!", "shit", "Shit indeed!")
	}
bot = None #this will be set by the bot that loads the module
