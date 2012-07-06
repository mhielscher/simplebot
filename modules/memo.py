#!/usr/bin/python

import irclib
import time

memos = {}

def on_join(c, e):
	nick = irclib.nm_to_n(e.source())
	if bot._quietmode:
		t = irclib.nm_to_n(e.source())
	else:
		t = e.target()
	print bot._quietmode, t
	if nick in memos:
		c.privmsg(t, "Memos for "+nick+":")
		for msg in memos[nick]:
			c.privmsg(t, msg)
			time.sleep(3)
		del memos[nick]

def save_memo(c, s, t, ch, a):
	#memo <nick> <message>
	nick = a[0]
	message = ' '.join(a[1:])
	if nick not in memos:
		memos[nick] = []
	memos[nick].append("<%s> %s" % (s, message))
	c.privmsg(t, "Memo added for "+nick+".")
	
botmodulename = "memo"
commands = {
	"memo" : (save_memo, 0)
	}
hooks = {
	"join" : on_join
	}
help = {
	"memo" : ("Saves a memo for an absent user.", "memo <nick> <message>", "Saves a memo, <message>, to be displayed when <nick> joins a channel.")
	}
bot = None #this will be set by the bot that loads the module
