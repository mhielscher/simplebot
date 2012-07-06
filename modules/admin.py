#!/usr/bin/python

import time
import datetime
import threading
import re

def on_whoisuser(c, e):
	print "Whois:", e.source(), e.target(), e.arguments()
	for req in bot.outstandingrequests:
		if "whois" in req.waitingfor():
			if req.request() == "ban":
				nick = req.arguments()[0]
				if e.arguments()[0] == nick:
					if req.mode == "-nick":
						mask = e.arguments()[0]+"!*@*"
						execute_ban(c, req.target(), mask, req.time)
					elif req.mode == "-username":
						mask = "*!"+e.arguments()[1]+"@*"
						execute_ban(c, req.target(), mask, req.time)
					elif req.mode == "-hostmask":
						mask = "*!*@"+e.arguments()[2]
						execute_ban(c, req.target(), mask, req.time)
					else:
						bot.replyError(c, req.target(), "ERROR: Invalid ban mode.")
					bot.outstandingrequests.remove(req)
			elif req.request() == "unban":
				nick = req.arguments()[0]
				if e.arguments()[0] == nick:
					req.data().nick = e.arguments()[0]
					req.data().username = e.arguments()[1]
					req.data().hostname = e.arguments()[2]
					if req.banmask != None:
						execute_unban(c, req)

def on_banlist(c, e):
	print "Banlist: ", e.source(), e.target(), e.arguments()
	for req in bot.outstandingrequests:
		if "banlist" in req.waitingfor():
			if req.request() == "unban":
				req.banmask = e.arguments()[1]
				if req.data().nick != None:
					execute_unban(c, req)

def parse_time(t):
	if t.startswith("+"):
		m = re.search(r"\+(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?", t)
		dys = m.group(1) or 0
		hrs = m.group(2) or 0
		mins = m.group(3) or 0
		secs = m.group(4) or 0
		td = datetime.timedelta(days=int(dys), seconds=int(secs), minutes=int(mins), hours=int(hrs))
		return time.mktime((datetime.datetime.now()+td).timetuple())
	else:
		p = subprocess.Popen(['date', '+%s.%N', "--date=%s" % t], stdout=subprocess.PIPE)
		out = float(p.stdout.read())
		return out

def validatechanop(c, t, chan):
	if chan and bot.channels[chan].is_oper(bot._nickname):
		return True
	elif not chan:
		c.privmsg(t, "You didn't specify a channel.")
	else:
		c.privmsg(t, "I am not a chanop in "+chan+".")
		return False

def do_op(c, s, t, ch, a):
	if len(a) < 1:
		nick = s
	else:
		nick = a[0]
	validatechanop(c, t, ch) and c.mode(ch, "+o "+nick)

def do_deop(c, s, t, ch, a):
	if len(a) < 1:
		nick = s
	else:
		nick = a[0]
	validatechanop(c, t, ch) and c.mode(ch, "-o "+nick)

def do_voice(c, s, t, ch, a):
	if len(a) < 1:
		nick = s
	else:
		nick = a[0]
	validatechanop(c, t, ch) and c.mode(ch, "+v "+nick)

def do_devoice(c, s, t, ch, a):
	if len(a) < 1:
		nick = s
	else:
		nick = a[0]
	validatechanop(c, t, ch) and c.mode(ch, "-v "+nick)

def do_kick(c, s, t, ch, a):
	nick = a[0]
	comment = " ".join(a)
	validatechanop(c, t, ch) and c.kick(ch, nick, comment)

def do_ban(c, s, t, ch, a):
	"""
		Command takes a nick as target. Default is to ban by
		hostmask, which means we have to find the hostmask
		currently associated with the nick. We'll send a whois
		and wait for a whoisserver reply, then from there
		kick it back to the real ban function.
		ban [channel] <nick> [-mode] [time]
	"""
	nick = a[0]
	print "Ban: ",t,a
	if validatechanop(c, t, ch):
		if len(a) > 1:
			if len(a) >= 3:
				if a[1].startswith("-"):
					mode = a[1]
					tm = " ".join(a[2:])
				else:
					mode = "-hostmask"
					tm = " ".join(a[1:])
			else:
				if a[1].startswith("-"):
					mode = a[1]
					tm = None
				else:
					mode = "-hostmask"
					tm = a[1]
		else:
			mode = "-hostmask"
			tm = None
		print "Ban: ",t,a
		c.whois([nick])
		r = bot.Request("ban", t, ["whois"], [nick], bot.WhoisData(nick))
		bot.outstandingrequests.append(r)
		r.mode = mode
		r.time = tm
		r.channel = ch

def execute_ban(c, channel, mask, t):
	print "Executing ban: ", channel, mask, t
	c.mode(channel, "+b "+mask)
	if t:
		tm = parse_time(t)
		timer = threading.Timer(tm-time.time(), remove_ban, [c, channel, mask])
		print "Timer: ", time.time(), tm, tm-time.time()
		timer.start()

def do_unban(c, s, t, ch, a):
	nick = a[0]
	print "Unban: ",t,a
	if validatechanop(c, t, ch):
		c.whois([nick])
		c.mode(ch, "+b")
		r = bot.Request("unban", t, ["whois", "banlist"], [nick], bot.WhoisData(nick))
		bot.outstandingrequests.append(r)
		r.channel = ch
		r.banmask = None

def execute_unban(c, req):
	banre = req.banmask.replace(".", r"\.")
	banre = banre.replace("*", ".*?")
	nickmask = req.data().nick+"!"+req.data().username+"@"+req.data().hostname
	m = re.match(banre, nickmask)
	if m != None:
		remove_ban(c, req.channel, req.banmask)
	bot.outstandingrequests.remove(req)

def remove_ban(c, channel, mask):
	print "Removing ban: ", channel, mask
	c.mode(channel, "-b "+mask)

def do_kickban(c, s, t, ch, a):
	# kickban [channel] <nick> [-mode] [[+]time] [: comment]
	banargs = []
	kickargs = []
	nick = a[0]
	banargs.append(nick)
	kickargs.append(nick)
	print "Kickban: ",t,a
	if validatechanop(c, t, ch):
		if len(a) > 1 and a[1].startswith("-"):
			mode = a[1]
			a = a[2:]
		else:
			mode = "-hostmask"
			a = a[1:]
		if len(a) > 0:
			if a[0] == ':':
				a[0] = ' :'
		a = " ".join(a).split(" : ")
		tm = a[0]
		if len(a) > 1:
			comment = a[1]
		else:
			comment = ''
		banargs.append(mode)
		if tm != '':
			banargs += tm.split()
		kickargs += comment.split()
		do_ban(c, s, t, ch, banargs)
		#use a Timer here for short delay because we have to wait
		#for the whois and banlist data to come back
		timer = threading.Timer(0.5, do_kick, [c, s, t, ch, kickargs])
		timer.start()


botmodulename = "admin"
commands = {
	"op" : (do_op, 10),
	"deop" : (do_deop, 10),
	"voice" : (do_voice, 10),
	"devoice" : (do_devoice, 10),
	"kick" : (do_kick, 10),
	"ban" : (do_ban, 10),
	"unban" : (do_unban, 10),
	"kickban" : (do_kickban, 10)
	}
hooks = {
	"whoisuser" : on_whoisuser,
	"banlist" : on_banlist
	}
help = {
	"op" : ("Gives ops to a user.", "op [channel] <nick>", "Gives channel operator status to user <nick> in [channel]."),
	"deop" : ("Removes ops from a user.", "deop [channel] <nick>", "Removes channel operator status from user <nick> in [channel]."),
	"voice" : ("Gives voice to a user.", "voice [channel] <nick>", "Gives voice to user <nick> in [channel]."),
	"devoice" : ("Removes voice from a user.", "devoice [channel] <nick>", "Removes voice from user <nick> in [channel]."),
	"kick" : ("Kicks a user.", "kick [channel] <nick> [reason]", "Kicks user <nick> from [channel], citing [reason]."),
	"ban" : ("Bans a user.", "ban [channel] <nick> [-mode] [[+]time]", "Bans user <nick> from [channel] by [-hostmask] (default), [-username], or [-nick], until [time] or for [+time] amount."),
	"unban" : ("Removes all bans against a user.", "unban [channel] <nick>", "Removes all bans on <nick>."),
	"kickban" : ("Kicks and bans a user.", "kickban [channel] <nick> [-mode] [[+]time] : [reason]", "Combines kick and ban commands (see individual commands for option details).")
	}
bot = None #this will be set by the bot that loads the module
