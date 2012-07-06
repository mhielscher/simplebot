#!/usr/bin/python

import time
import re
import urllib
import httplib
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

def search(query): 
	"""Search using AjaxSearch, and return its JSON."""
	#uri = 'http://ajax.googleapis.com/ajax/services/search/web'
	args = '?v=1.0&rsz=large&safe=off&key=ABQIAAAA8PWlisHfSlzZquDVelObURS-NT9rF_DfcID2uEUYiRA2x2mF8xQW0IUsMPiwbFt1r_aEf0zcGg9HfQ&q=' + urllib.quote(query.encode('utf-8'))
	conn = httplib.HTTPConnection('ajax.googleapis.com')
	conn.request('GET', '/ajax/services/search/web'+args)
	r = conn.getresponse()
	bytes = r.read()
	return json(bytes)

def result(query): 
	results = search(query)
	try: return results['responseData']['results'][0]['unescapedUrl']
	except IndexError: return None

def count(query): 
	results = search(query)
	if not results.has_key('responseData'): return '0'
	if not results['responseData'].has_key('cursor'): return '0'
	if not results['responseData']['cursor'].has_key('estimatedResultCount'): 
	  return '0'
	return results['responseData']['cursor']['estimatedResultCount']

def formatnumber(n): 
	"""Format a number with beautiful commas."""
	parts = list(str(n))
	for i in range((len(parts) - 3), 0, -3):
		parts.insert(i, ',')
	return ''.join(parts)

def do_search(c, s, t, ch, a): 
	"""Queries Google for the specified input."""
	query = " ".join(a)
	if not query: 
		return bot.replyError(c, t, "ERROR: no search terms specified")
	uri = result(query)
	if uri: 
		c.privmsg(t, dodgefilter.url(uri, ch))
		#if not hasattr(phenny.bot, 'last_seen_uri'):
		#	phenny.bot.last_seen_uri = {}
		#phenny.bot.last_seen_uri[input.sender] = uri
	else: c.privmsg(t, "No results found for '%s'." % query)

def do_count(c, s, t, ch, a): 
	"""Returns the number of Google results for the specified input."""
	query = " ".join(a)
	if not query: 
		return bot.replyError(c, t, "ERROR: no search terms specified")
	num = formatnumber(count(query))
	c.privmsg(t, query + ': ' + num)


botmodulename = "search"
commands = {
	"google" : (do_search, 0),
	"gcount" : (do_count, 0)
	}
help = {
	"google" : ("Searches Google and returns the first result.", "google <terms>", "Searches Google for <terms> and returns the URL of the first result."),
	"gcount" : ("Returns number of Google results for a search term.", "gcount <terms>", "Searches Google for <terms> and returns the estimated number of search results.")
	}
bot = None #this will be set by the bot that loads the module
