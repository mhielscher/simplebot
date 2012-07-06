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

def do_shorten(c, s, t, ch, a):
	url = ''.join(a)
	args = '?format=json&version=2.0.1&login=%s&apiKey=%s&longUrl=%s' % ("restorer", "R_70aec10678b8929cac02911479bfc9e7", url)
	conn = httplib.HTTPConnection('api.bit.ly')
	conn.request('GET', '/shorten'+args)
	r = conn.getresponse()
	bytes = r.read()
	results = json(bytes)
	print results
	tinyurl = results['results'][url]['shortUrl']
	c.privmsg(t, dodgefilter.url(tinyurl, ch))
	
'''
{u'errorCode': 0,
u'errorMessage': u'',
u'results':
	{u'http://en.wikipedia.org/':
		{u'shortKeywordUrl': u'',
		u'hash': u'4f0TzR',
		u'userHash': u'7ic996',
		u'shortUrl':
		u'http://bit.ly/7ic996'}
	}, 
u'statusCode': u'OK'}
'''

botmodulename = "shortenurl"
commands = {
	"shortenurl" : (do_shorten, 0)
	}
help = {
	"shortenurl" : ("Shortens a URL using bit.ly and prints the short URL.", "shortenurl <URL>", "Shortens <URL> using bit.ly and prints it.")
	}
bot = None #this will be set by the bot that loads the module
