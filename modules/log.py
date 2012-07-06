#!/usr/bin/python

import time
import datetime
import irclib

lognames = {}
currentday = {}

logprivmsg = False
logdirectory = "./"

def timestamp():
	# for now, a set format. Customization will come later
	return time.strftime("%H:%M:%S")

def check_day_change(c, e):
	if e.target() not in lognames.keys() or e.target() not in currentday.keys():
		return
	if datetime.date.today() != currentday[e.target()]:
		log = lognames.get(e.target(), None)
		if log == None:
			return
		logfile = open(logdirectory+log, 'a')
		print >>logfile, "--- Day changed %s" % (time.strftime("%a %b %d %Y"))
		logfile.close()
		currentday[e.target()] = datetime.date.today()

def on_join(c, e):
	# temporary for now, until I figure out config options
	if irclib.nm_to_n(e.source()) == bot._nickname:
		lognames[e.target()] = e.target()+".log"
	log = lognames.get(e.target(), None)
	if log == None:
		return
	logfile = open(logdirectory+log, 'a')
	if irclib.nm_to_n(e.source()) == bot._nickname:
		print >>logfile, "-- Log opened %s" % (time.strftime("%a %b %d %Y %H:%M:%S %Z"))
		currentday[e.target()] = datetime.date.today()
	print >>logfile, "%s -!- %s [%s] has joined %s" % (timestamp(), irclib.nm_to_n(e.source()), irclib.nm_to_uh(e.source()), e.target())
	logfile.close()

def on_pubmsg(c, e):
	log = lognames.get(e.target(), None)
	if log == None:
		return
	logfile = open(logdirectory+log, 'a')
	nick = irclib.nm_to_n(e.source())
	utype = ' '
	if bot.channels[e.target()].is_oper(nick):
		utype = '@'
	elif bot.channels[e.target()].is_voiced(nick):
		utype = '+'
	print >>logfile, "%s<%s%s> %s" % (timestamp(), utype, nick, e.arguments()[0])
	logfile.close()

def on_action(c, e):
	log = lognames.get(e.target(), None)
	if log == None:
		return
	logfile = open(logdirectory+log, 'a')
	nick = irclib.nm_to_n(e.source())
	utype = ' '
	if bot.channels[e.target()].is_oper(nick):
		utype = '@'
	elif bot.channels[e.target()].is_voiced(nick):
		utype = '+'
	print >>logfile, "%s * %s %s" % (timestamp(), nick, e.arguments()[0])
	logfile.close()

def on_privmsg(c, e):
	if logprivmsg:
		nick = irclib.nm_to_n(e.source())
		log = nick+".priv.log"
		logfile = open(logdirectory+log, 'a')
		print >>logfile, "%s<%s> %s" % (timestamp(), nick, e.arguments()[0])
		logfile.close()

def on_mode(c, e):
	log = lognames.get(e.target(), None)
	if log == None:
		return
	logfile = open(logdirectory+log, 'a')
	print >>logfile, "%s -!- mode/%s [%s %s] by %s" % (timestamp(), e.target(), e.arguments()[0], ' '.join(e.arguments()[1:]), irclib.nm_to_n(e.source()))
	logfile.close()

def on_part(c, e):
	log = lognames.get(e.target(), None)
	if log == None:
		return
	logfile = open(logdirectory+log, 'a')
	partreason = ""
	try:
		partreason = e.arguments()[0]
	except IndexError:
		partreason = "Client quit"
	print >>logfile, "%s -!- %s [%s] has left %s [%s]" % (timestamp(), irclib.nm_to_n(e.source()), irclib.nm_to_uh(e.source()), e.target(), partreason)
	if irclib.nm_to_n(e.source()) == bot._nickname:
		print >>logfile, "-- Log closed %s" % (time.strftime("%a %b %d %Y %H:%M:%S %Z"))
		del currentday[e.target()]
	logfile.close()

def on_quit(c, e):
	log = lognames.get(e.target(), None)
	if log == None:
		return
	logfile = open(logdirectory+log, 'a')
	quitreason = ""
	try:
		quitreason = e.arguments()[0]
	except IndexError:
		quitreason = "Client quit"
	print >>logfile, "%s -!- %s [%s] has quit [%s]" % (timestamp(), irclib.nm_to_n(e.source()), irclib.nm_to_uh(e.source()), quitreason)
	if irclib.nm_to_n(e.source()) == bot._nickname:
		print >>logfile, "-- Log closed %s" % (time.strftime("%a %b %d %Y %H:%M:%S %Z"))
		del currentday[e.target()]
	logfile.close()

def on_kick(c, e):
	log = lognames.get(e.target(), None)
	if log == None:
		return
	logfile = open(logdirectory+log, 'a')
	print >>logfile, "%s -!- %s was kicked from %s by %s [%s]" % (timestamp(), e.arguments()[0], e.target(), e.source(), e.arguments()[1])
	if e.arguments()[0] == bot._nickname:
		print >>logfile, "-- Log closed %s" % (time.strftime("%a %b %d %Y %H:%M:%S %Z"))
		del currentday[e.target()]
	logfile.close()

botmodulename = "log"
hooks = {
	"all_events" : check_day_change,
	"join" : on_join,
	"pubmsg" : on_pubmsg,
	"privmsg" : on_privmsg,
	"action" : on_action,
	"mode" : on_mode,
	"part" : on_part,
	"quit" : on_quit,
	"kick" : on_kick
	}
bot = None #this will be set by the bot that loads the module

def on_load():
	global logdirectory
	if not logdirectory.endswith('/'):
		logdirectory += '/'
