#!/usr/bin/python

import sys
import os
import subprocess

if "./modules/" not in sys.path:
	sys.path.append("./modules/")
import dodgefilter

#default values
pisgpath = "/usr/bin/pisg"
statsurl = "http://www.wasabiflux.org/bot/stats/"

def chan_to_file(chan):
	f = chan.replace('#', '')+'.html'
	return f

def generate_stats(c, s, t, ch, a):
	r = subprocess.call([pisgpath, '-co', bot.basedir+"/config/default.pisg.conf"])
	if r == 0:
		c.privmsg(t, "Stats updated: "+dodgefilter.url(statsurl+chan_to_file(ch), ch))
	else:
		c.privmsg(t, "Error running pisg (probably a config error?). Stats not updated.")

def print_url(c, s, t, ch, a):
	c.privmsg(t, "Stats: "+dodgefilter.url(statsurl+chan_to_file(ch), ch))
	
def on_load():
	global configfile
	global bot
	if not configfile.startswith('/'):
		if configfile.startswith('./'):
			configfile = configfile[2:]
		configfile = bot.basedir+'/'+configfile

botmodulename = "stats"
commands = {
	"stats" : (generate_stats, 1),
	"statsurl" : (print_url, 0)
	}
help = {
	"stats" : ("Generates new stats and prints the URL.", "stats [channel]", "Generates new stats for [channel] (or current channel), and prints the URL."),
	"statsurl" : ("Prints the stats URL.", "statsurl [channel]", "Prints the URL for channel stats without generating new stats.")
	}
bot = None #this will be set by the bot that loads the module
configfile = "./config/default.pisg.conf"
