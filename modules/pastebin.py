#!/usr/bin/python

import re
import httplib
import urllib
import sys

if "./modules/" not in sys.path:
	sys.path.append("./modules/")
import dodgefilter

linkexp = r'<li><a href="(http://.*?)">(NICK)</a><br/>'

def check_pastebin(c, s, t, ch, a):
	if len(a) > 0:
		nick = a[0]
	else:
		nick = '.*?'
	linkre = re.compile(linkexp.replace("NICK", nick))
	conn = httplib.HTTPConnection(subdomain+'.pastebin.com')
	conn.request('GET', '/')
	r = conn.getresponse()
	bytes = r.read()
	if nick == ".*?":
		l = linkre.findall(bytes)
		for pair in l:
			if pair[1] in bot.channels[ch].users():
				c.privmsg(t, "Recent pastebin by "+pair[1]+": "+dodgefilter.url(pair[0], ch))
				break
		else:
			c.privmsg(t, "No recent pastebin by anyone in "+ch+".")
	else:
		m = linkre.search(bytes)
		if m:
			c.privmsg(t, "Recent pastebin by "+nick+": "+dodgefilter.url(m.group(1), ch))
		else:
			c.privmsg(t, "No recent pastebin by "+nick+".")

botmodulename = "pastebin"
commands = {
	"pbmostrecent" : (check_pastebin, 0)
	}
help = {
	"pbmostrecent" : ("Finds the most recent pastebin by a user on a channel.", "pbmostrecent [channel] [nick]", "Checks for a recent pastebin from [nick], or any nick in [channel].")
	}
bot = None #this will be set by the bot that loads the module
subdomain = "simplebot"
