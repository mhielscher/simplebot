#!/usr/bin/python

import time
import irclib

lastseen = {}

def on_whoisuser(c, e):
	print "Whois:", e.source(), e.target(), e.arguments()
	for req in bot.outstandingrequests:
		if "whois" in req.waitingfor():
			if req.request() == "seen":
				nick = req.arguments()[0]
				if e.arguments()[0] == nick:
					req.data().nick = e.arguments()[0]
					req.data().username = e.arguments()[1]
					req.data().hostname = e.arguments()[2]
					req.data().realname = e.arguments()[3]

def on_whoisserver(c, e):
	for req in bot.outstandingrequests:
		if "whois" in req.waitingfor():
			if req.request() == "seen":
				nick = req.arguments()[0]
				if e.arguments()[0] == nick:
					req.data().server = e.arguments()[1]
					req.data().serverinfo = e.arguments()[2]

def on_whoisoperator(c, e):
	for req in bot.outstandingrequests:
		if "whois" in req.waitingfor():
			if req.request() == "seen":
				nick = req.arguments()[0]
				if e.arguments()[0] == nick:
					req.data().op = True

def on_whoisidle(c, e):
	for req in bot.outstandingrequests:
		if "whois" in req.waitingfor():
			if req.request() == "seen":
				nick = req.arguments()[0]
				if e.arguments()[0] == nick:
					req.data().idle = int(arguments()[1])

def on_whoischannels(c, e):
	print "Channels:", e.source(), e.target(), e.arguments()
	for req in bot.outstandingrequests:
		if "whois" in req.waitingfor():
			if req.request() == "seen":
				nick = req.arguments()[0]
				if e.arguments()[0] == nick:
					pass

def on_320(c, e):
	print "Got 320:", e.eventtype(), e.source(), e.target(), e.arguments()
	for req in bot.outstandingrequests:
		if "whois" in req.waitingfor():
			if req.request() == "seen":
				nick = req.arguments()[0]
				if e.arguments()[0] == nick:
					req.data().extra.append(e.arguments()[1])

def on_endofwhois(c, e):
	print "End of Whois"
	for req in bot.outstandingrequests:
		if "whois" in req.waitingfor():
			if req.request() == "seen":
				nick = req.arguments()[0]
				if e.arguments()[0] == nick:
					c.privmsg(req.target(), "I have not seen "+nick+", but he/she is currently online.")
					bot.outstandingrequests.remove(req)

def on_nick(c, e):
	lastseen[e.arguments()[0]] = (e.target(), time.localtime())

def on_nosuchnick(c, e):
	for req in bot.outstandingrequests:
		if "whois" in req.waitingfor():
			if req.request() == "seen":
				nick = req.arguments()[0]
				if e.arguments()[0] == nick:
					c.privmsg(req.target(), nick+" has never been seen.")
					bot.outstandingrequests.remove(req)

def on_join(c, e):
	if irclib.nm_to_n(e.source()) != bot._nickname:
		lastseen[irclib.nm_to_n(e.source())] = (e.target(), time.localtime())

def on_part(c, e):
	print "Part: ", e.source(), e.target(), e.arguments()
	lastseen[irclib.nm_to_n(e.source())] = (e.target(), time.localtime())
	
def on_quit(c, e):
	lastseen[irclib.nm_to_n(e.source())] = (e.target(), time.localtime())

def do_seen(c, s, t, ch, a):
	nick = a[0]
	where = None
	for chan in bot.channels:
		for user in bot.channels[chan].users():
			if nick == user:
				if where == None:
					where = []
				where.append(chan)
		if where != None:
			msg = nick+" is currently in "+(", ".join(where))+"."
			if len(where) > 1:
				msg = msg[:msg.rindex(" ")]+" and"+msg[msg.rindex(" "):]
			c.privmsg(t, msg)
			break
	if where == None:
		for user, (chan, tm) in lastseen.iteritems():
			if nick == user:
				where = chan
				c.privmsg(t, nick+" was last seen in "+chan+" at "+time.strftime("%H:%M:%S %Z %a %b %d %Y", tm))
				break
	if where == None:
		c.whois([nick])
		bot.outstandingrequests.append(bot.Request("seen", t, ["whois"], [nick], bot.WhoisData(nick)))
	
botmodulename = "seen"
commands = {
	"seen" : (do_seen, 0)
	}
hooks = {
	"whoisuser" : on_whoisuser,
	"whoisserver" : on_whoisserver,
	"whoisoperator" : on_whoisoperator,
	"whoisidle" : on_whoisidle,
	"whoischannels" : on_whoischannels,
	"320" : on_320,
	"endofwhois" : on_endofwhois,
	"nosuchnick" : on_nosuchnick,
	"join" : on_join,
	"part" : on_part,
	"quit" : on_quit
	}
help = {
	"seen" : ("Prints last time a user was seen.", "seen <nick>", "Prints the last time and place <nick> was seen.")
	}
bot = None #this will be set by the bot that loads the module
