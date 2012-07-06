#!/usr/bin/python

import re

urlre = re.compile(r"^(https?://)?((\w+\.)*)(\w+)(\.\w+)(/.*)$")

def url(url, ch=None):
	print "Channel: %s" % (ch)
	if ch == None or bot.channels[ch].has_mode('U'):
		m = urlre.match(url)
		decens = urlre.sub(r"\2 \4 \5 \6", url)
		decens = decens.replace(".", " . ")
		return decens
	else:
		return url
	
def censor(word, ch=None):
	print "Channel: %s" % (ch)
	if ch == None or bot.channels[ch].has_mode('G'):
		# quasi-leetspeak converter
		dodged = word.replace("o", "0")
		dodged = dodged.replace("e", "3")
		dodged = dodged.replace("l", "1")
		dodged = dodged.replace("a", "4")
		dodged = dodged.replace("s", "5")
		dodged = dodged.replace("u", "v")
		for i in xrange(2, len(dodged), 3):
			dodged = dodged[:i]+'*'+dodged[i:]
		return dodged
	else:
		return word

def dodge_url(c, s, t, ch, a):
	if ch:
		targ = ch
	else:
		targ = t
	c.privmsg(targ, "URL from %s: %s" % (s, url(''.join(a))))

def dodge_censor(c, s, t, ch, a):
	if ch:
		targ = ch
	else:
		targ = t
	c.privmsg(targ, "Decensored from %s: %s" % (s, censor(' '.join(a))))
	

botmodulename = "dodgefilter"
commands = {
	"dodgeurl" : (dodge_url, 0),
	"dodgecensor" : (dodge_censor, 0)
	}
help = {
	"dodgeurl" : ("Transforms a URL to evade the URL filter.", "dodgeurl <channel> <URL>", "Sends a modified <URL> to <channel> to evade the filter. Send command directly to bot."),
	"dodgecensor" : ("Transforms a swear word to evade the filter.", "dodgecensor <channel> <word>", "Sends a modified <word> to <channel> to evade the filter. Send command directly to bot.")
	}
bot = None #this will be set by the bot that loads the module
