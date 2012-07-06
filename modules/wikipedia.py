#!/usr/bin/python

import re
import httplib
import urllib
import sys

if "./modules/" not in sys.path:
	sys.path.append("./modules/")
import dodgefilter

r_string = re.compile(r'("(\\.|[^"\\])*")')
r_json = re.compile(r'^[,:{}\[\]0-9.\-+Eaeflnr-u \n\r\t]+$')
env = {'__builtins__': None, 'null': None, 'true': True, 'false': False}

def json(text): 
	"""Evaluate JSON text safely (we hope)."""
	if r_json.match(r_string.sub('', text)): 
		text = r_string.sub(lambda m: 'u' + m.group(1), text)
		return eval(text.strip(' \t\r\n'), env, {})
	raise ValueError('Input must be serialised JSON.')

def do_wiki(c, s, t, ch, a):
	query = ' '.join(a)
	args = '?format=json&action=opensearch&search=' + urllib.quote(query.encode('utf-8'))
	conn = httplib.HTTPConnection('en.wikipedia.org')
	conn.request('GET', '/w/api.php'+args)
	r = conn.getresponse()
	bytes = r.read()
	results = json(bytes)
	if len(results[1])>0:
		title = results[1][0].replace(' ', '_')
		url = "http://en.wikipedia.org/wiki/"+title
		c.privmsg(t, dodgefilter.url(url, ch))
	else:
		c.privmsg(t, "No matching articles.")

botmodulename = "wikipedia"
commands = {
	"wikipedia" : (do_wiki, 0)
	}
help = {
	"wikipedia" : ("Looks up an article on wikipedia.", "wikipedia <subject>", "Searches for <subject> on wikipedia and returns a URL to a matching article.")
	}
bot = None #this will be set by the bot that loads the module
