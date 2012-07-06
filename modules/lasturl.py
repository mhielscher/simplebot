#!/usr/bin/python

import re
import sys

if "./modules/" not in sys.path:
	sys.path.append("./modules/")
import dodgefilter

rs = r"(^| )(https?://.*?)( |$)"
#rs = r'''(?#Protocol)(?:(?:ht|f)tp(?:s?)\:\/\/|~/|/)?(?#Username:Password)(?:\w+:\w+@)?(?#Subdomains)(?:(?:[-\w]+\.)+(?#TopLevel Domains)(?:com|org|net|gov|mil|biz|info|mobi|name|aero|jobs|museum|travel|[a-z]{2}))(?#Port)(?::[\d]{1,5})?(?#Directories)(?:(?:(?:/(?:[-\w~!$+|.,=]|%[a-f\d]{2})+)+|/)+|\?|#)?(?#Query)(?:(?:\?(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)(?:&(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)*)*(?#Anchor)(?:#(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)?'''
urlre = re.compile(rs)

lasturl = {}

def on_pubmsg(c, e):
	m = urlre.search(e.arguments()[0])
	if m:
		lasturl[e.target()] = m.group(2)

def do_lasturl(c, s, t, ch, a):
	lu = lasturl.get(ch, "None seen.")
	c.privmsg(t, "Last URL: "+dodgefilter.url(lu, ch))

botmodulename = "lasturl"
commands = {
	"lasturl" : (do_lasturl, 0)
	}
hooks = {
	"pubmsg" : on_pubmsg
	}
help = {
	"lasturl" : ("Prints the last URL seen.", "lasturl [channel]", "Prints the last URL seen in [channel], or the current channel.")
	}
bot = None #this will be set by the bot that loads the module
