#!/usr/bin/python

import re
import sys
import time
import irclib
import threading

if "./modules/" not in sys.path:
	sys.path.append("./modules/")
import admin

capsre = re.compile(r"[a-z]")

watchlist = {}

def unsilence(c, ch, n):
	if n in bot.channels[ch].users():
		admin.validatechanop(c, ch, ch) and c.mode(ch, "+v "+n)
		c.privmsg(ch, "%s, you may speak again. Please be respectful.")

def on_pubmsg(c, e):
	global watchlist
	nick = irclib.nm_to_n(e.source())
	if not capsre.search(e.arguments()[0]):
		print "Caught CAPS"
		if nick in watchlist:
			watchlist[nick][0] += 1
			watchlist[nick][1] = time.time()
		else:
			watchlist[nick] = [1, time.time()]
		if watchlist[nick] == 3:
			c.privmsg(e.target(), "%s, please drop the caps or you will be silenced." % (nick))
		elif watchlist[nick] == 5:
			admin.validatechanop(c, e.target(), e.target()) and c.mode(e.target(), "-v "+nick)
			c.privmsg(e.target(), "%s, it's rude to continually speak in all caps." % (nick))
			c.privmsg(e.target(), "You have been silenced for 3 minutes.")
			timer = threading.Timer(180, unsilence, [c, e.target(), nick])
			timer.start()
		elif watchlist[nick] == 6:
			c.privmsg(e.target(), "%s, remember, no yelling. There will not be another warning." % (nick))
		elif watchlist[nick] == 8:
			admin.validatechanop(c, e.target(), e.target()) and c.mode(e.target(), "-v "+nick)
			c.privmsg(e.target(), "Good job, %s. You just got yourself banned.")
			time.sleep(3)
			admin.do_kickban(c, bot._nickname, e.target(), e.target(), [nick, "+2h"])
	else:
		if nick in watchlist and watchlist[nick][1]-time.time() > 10:
			watchlist[nick][0] -= 1
			watchlist[nick][1] = time.time()
			if watchlist[nick][0] == 0:
				del watchlist[nick]
			

botmodulename = "capsguard"
commands = {
	}
hooks = {
	"pubmsg" : on_pubmsg
	}
help = {
	}
bot = None #this will be set by the bot that loads the module
