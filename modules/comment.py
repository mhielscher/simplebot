#!/usr/bin/python

import re
import sys
import random

responses = {}

def on_pubmsg(c, e):
	for w in responses:
		if e.arguments()[0].find(w) != -1:
			c.privmsg(e.target(), random.choice(responses[w]))

def do_addresponse(c, s, t, ch, a):
	line = ' '.join(a)
	pl = line.split('"')
	tl = []
	for i in range(0, len(pl), 2):
		tl += pl[i].split(' ')
		if i+1 < len(pl):
			tl.append(pl[i+1])
	tl = filter(lambda t:t!='', tl)
	if tl[0] in responses:
		responses[tl[0]].append(tl[1])
	else:
		responses[tl[0]] = [tl[1]]
	c.privmsg(t, "I'll remember that.")

def do_listresponses(c, s, t, ch, a):
	if len(a) > 0:
		line = ' '.join(a)
		pl = line.split('"')
		tl = []
		for i in range(0, len(pl), 2):
			tl += pl[i].split(' ')
			if i+1 < len(pl):
				tl.append(pl[i+1])
		tl = filter(lambda t:t!='', tl)
		c.privmsg(t, 'Responses to "%s":' % (tl[0]))
		for r, i in zip(responses[tl[0]], range(1, len(responses[tl[0]])+1)):
			c.privmsg(t, "%d:   %s" % (i, r))
	else:
		for w in responses:
			c.privmsg(t, 'Responses to "%s":' % (w))
			for r, i in zip(responses[w], range(1, len(responses[w])+1)):
				c.privmsg(t, "%d:   %s" % (i, r))

def do_delresponse(c, s, t, ch, a):
	if len(a) < 1:
		c.privmsg(t, "More arguments needed.")
	pl = line.split('"')
	tl = []
	for i in range(0, len(pl), 2):
		tl += pl[i].split(' ')
		if i+1 < len(pl):
			tl.append(pl[i+1])
	tl = filter(lambda t:t!='', tl)
	if tl[0] in responses:
		try:
			del responses[tl[0]][int(tl[1])]
		except ValueError:
			c.privmsg(t, "Invalid arguments. Form: delcomment [phrase] [number]")
	else:
		c.privmsg(t, "%s not a current trigger phrase." % (tl[0]))
	c.privmsg(t, "I'll forget that response.")
		

botmodulename = "comment"
commands = {
	"addcomment" : (do_addresponse, 1),
	"listcomments" : (do_listresponses, 0),
	"delcomment" : (do_delresponse, 1)
	}
hooks = {
	"pubmsg" : on_pubmsg
	}
help = {
	"addcomment" : ("Adds a response to a word or phrase.", 'addcomment "word or phrase" "The response."', "Adds a response to be chosen randomly when the listed word or phrase is heard."),
	"listcomments" : ("Lists the comments associated with a word or phrase.", 'listcomments [phrase]', "Lists the comments associated with [phrase], or all comments."),
	"delcomment" : ("Deletes a comment associated with a phrase.", "delcomment [phrase] [number]", "Delete comment [number] from responses to [phrase]. (See listcomments.)")
	}
bot = None #this will be set by the bot that loads the module
