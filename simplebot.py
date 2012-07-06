#!/usr/bin/python

import ircbot
import irclib
import time
import datetime
import xml.dom.minidom
import traceback
import threading
import subprocess
import re
import httplib
import urllib
import os
import imp
import hashlib
import sys


class SimpleBot(ircbot.SingleServerIRCBot):
	class Request:
		def __init__(self, r, t, w, a, d, e=60):
			self._waitingfor = w
			self._request = r
			self._arguments = a
			self._target = t
			self._data = d
			self.expire = e #currently doesn't do anything
	
		def waitingfor(self):
			return self._waitingfor
	
		def request(self):
			return self._request
	
		def arguments(self):
			return self._arguments
	
		def target(self):
			return self._target
	
		def data(self):
			return self._data
		

	class WhoisData:
		def __init__(self, w):
			self.who = w
			self.nick = None
			self.username = None
			self.hostname = None
			self.realname = None
			self.server = None
			self.serverinfo = None
			self.op = False
			self.idle = None
			self.channels = []
			self.extra = []
			self.was = False
	
	class UserInfo:
		def __init__(self, n, ph, h=None, a=0):
			self._primarynick = n
			self._allowednicks = []
			self._hostmasks = []
			if h != None:
				self._hostmasks.append(h)
			self._flags = {}
			self._password = ph
			self._access_level = a
			self._active = False
	
		def primarynick(self):
			return self._primarynick
	
		def allowednicks(self):
			return self._allowednicks
	
		def is_allowednick(self, n):
			return n in self._allowednicks
	
		def addnick(self, n):
			self._allowednicks.append(n)
	
		def hostmasks(self):
			return self._hostmasks
	
		def is_hostmask(self, h):
			return h in self._hostmasks
	
		def addhostmask(self, h):
			self._hostmasks.append(h)
	
		def flags(self):
			return self._flags
	
		def setflag(self, flag):
			self._flags[flag] = 1
	
		def unsetflag(self, flag):
			del self._flags[flag]
	
		def checkpassword(self, p):
			d = hashlib.sha256()
			d.update(p)
			return self._password == d.hexdigest()
		
		def setpassword(self, p):
			d = hashlib.sha256()
			d.update(p)
			self._password = d.hexdigest()
			#print "PASSWORD CHANGED - COPY TO CONFIG: %s - %s" % (self._primarynick, d.hexdigest())
		
		def accesslevel(self):
			return self._access_level
		
		def setaccesslevel(self, l):
			self._access_level = l
			
		def isactive(self):
			return self._active
		
		def setactive(self, a):
			self._active = a

	def __init__(self, bd, configfilename):
		self.configfile = configfilename
		self.basedir = bd
		self.staticchannels = {}
		self.modules = {}
		self.users = {}
		self.basedir = os.getcwd()
		self.doc = None
		self._set_defaults()
		self._read_config(self.configfile)
		if self.password and self.password != '':
			ircbot.SingleServerIRCBot.__init__(self, [(self.server, int(self.port), self.password)], self._nickname, self._username)
		else:
			ircbot.SingleServerIRCBot.__init__(self, [(self.server, int(self.port))], self._nickname, self._username)
		self._init_commands()
		self._load_modules()
		#self._register_hooks()
		self.lastseen = {}
		self.outstandingrequests = []
		self.commandhistory = []
	
	def _set_defaults(self):
		self._nickname = "simplebot"
		self._username = "simplebot"
		self._quietmode = False
	
	def _load_one_module(self, name, opts):
		self._unload_module(name)
		mod = imp.load_source(name, "modules/"+name+".py")
		if not mod:
			return False
		if hasattr(mod, "botmodulename"):
			mod.bot = self
			for option, value in opts.iteritems():
				setattr(mod, option, value)
			self.modules[name] = mod
		if hasattr(mod, "on_load"):
			mod.on_load()
		if hasattr(mod, "commands"):
			self.commands.update(mod.commands)
		if hasattr(mod, "hooks"):
			for hook, func in mod.hooks.iteritems():
				self.connection.add_global_handler(hook, func)
		return True
	
	def _unload_module(self, name):
		if name in self.modules:
			mod = self.modules[name]
			if hasattr(mod, "commands"):
				for comm in mod.commands.keys():
					del self.commands[comm]
			if hasattr(mod, "hooks"):
				for hook, func in mod.hooks.iteritems():
					self.connection.remove_global_handler(hook, func)
			del self.modules[name]
			return True
		else:
			return False
	
	def _load_modules(self):
		#load modules specified in the config
		for name, opts in self.modules.iteritems():
			if not self._load_one_module(name, opts):
				print "Could not load module "+name
		"""
		#load all modules in the modules/ directory
		for filename in os.listdir("modules"):
			if filename.startswith('.') or filename.startswith('~') or not filename.endswith('.py'):
				continue
			name = os.path.basename(filename)[:-3]
			m = imp.load_source(name, "modules/"+filename)
			if hasattr(m, "botmodulename"):
				m.bot = self
				self.modules[m.botmodulename] = m
		"""
	
	def _init_commands(self):
		print "Initing commands"
		#builtin commands
		self.commands = {
			"login" : (self.do_login, 0),
			"passwd" : (self.do_setpassword, 0),
			"loadmod" : (self.do_load_module, 10),
			"unloadmod" : (self.do_unload_module, 10),
			"quiet" : (self.set_quietmode, 1),
			"nick" : (self.change_nick, 10),
			"history" : (self.do_history, 0),
			"status" : (self.do_status, 1),
			"help" : (self.do_help, 0),
			"reloadconfig" : (self.do_reloadconfig, 15),
			"saveconfig" : (self.do_saveconfig, 15),
			"quit" : (self.do_quit, 10)
		}
	
	def _register_hooks(self):
		for name, mod in self.modules.iteritems():
			if hasattr(mod, "hooks"):
				for hook, func in mod.hooks.iteritems():
					self.connection.add_global_handler(hook, func)
	
	def _read_config(self, filename):
		print "Reading config"
		self.doc = xml.dom.minidom.parse(filename)
		bot = self.doc.getElementsByTagName("bot")[0]
		for mod in bot.getElementsByTagName("module"):
			mod.normalize()
			#The dict will hold config options that will be
			#set up in the module when it's loaded.
			modname = str(mod.getAttribute("name"))
			self.modules[modname] = {}
			if mod.hasChildNodes():
				for option in mod.childNodes:
					if option.nodeType == xml.dom.Node.ELEMENT_NODE:
						option.normalize()
						self.modules[modname][str(option.localName)] = str(option.firstChild.data.strip())
		for serv in bot.getElementsByTagName("server"):
			serv.normalize()
			#server and port
			self.server = serv.getAttribute("address")
			self.port = serv.getAttribute("port")
			self.password = serv.getAttribute("pass")
			#nickname
			n = serv.getElementsByTagName("nick")
			if len(n)>0:
				nick = n[0]
				nick.normalize()
				self._nickname = str(nick.firstChild.data.strip()) #remove unicode
			#username
			u = serv.getElementsByTagName("username")
			if len(u)>0:
				username = u[0]
				username.normalize()
				self._username = str(username.firstChild.data.strip()) #remove unicode
			#quiet mode
			q = serv.getElementsByTagName("quiet")
			if len(q)>0:
				quietmode = q[0]
				if (quietmode.getAttribute("status") == "on"):
					self._quietmode = True
				else:
					self._quietmode = False
			#channels
			for chan in serv.getElementsByTagName("channel"):
				chan.normalize()
				channame = chan.getAttribute("name")
				self.staticchannels[channame] = ChannelProperties()
				notices = chan.getElementsByTagName("notice")
				for notice in notices:
					notice.normalize()
					self.staticchannels[channame].setNotice(notice.firstChild.data.strip())
				logs = chan.getElementsByTagName("log")
				for log in logs:
					if log.getAttribute("on") != "off":
						self.staticchannels[channame].setLog(log.getAttribute("file"))
		#user access levels
		for user in serv.getElementsByTagName("user"):
			user.normalize()
			n = user.getElementsByTagName("primarynick")[0]
			n.normalize()
			n = n.firstChild.data.strip()
			p = user.getElementsByTagName("passwdhash")[0]
			p.normalize()
			p = p.firstChild.data.strip()
			ui = self.UserInfo(n, p)
			for nick in user.getElementsByTagName("allowednick"):
				nick.normalize()
				ui.addnick(nick.firstChild.data.strip())
			for mask in user.getElementsByTagName("hostmask"):
				mask.normalize()
				ui.addhostmask(mask.firstChild.data.strip())
			for flag in user.getElementsByTagName("flag"):
				flag.normalize()
				ui.setflag(flag.firstChild.data.strip())
			for lvl in user.getElementsByTagName("accesslevel"):
				lvl.normalize()
				ui.setaccesslevel(int(lvl.firstChild.data.strip()))
			self.users[n] = ui
			for nick in ui.allowednicks():
				self.users[nick] = ui
	
	def _write_config(self, filename):
		print "Writing config"
		bot = self.doc.getElementsByTagName("bot")[0]
		for mod in bot.getElementsByTagName("module"):
			mod.normalize()
			#The dict will hold config options that will be
			#set up in the module when it's loaded.
			modname = str(mod.getAttribute("name"))
			self.modules[modname] = {}
			if mod.hasChildNodes():
				for option in mod.childNodes:
					if option.nodeType == xml.dom.Node.ELEMENT_NODE:
						option.normalize()
						self.modules[modname][str(option.localName)] = str(option.firstChild.data.strip())
		for serv in bot.getElementsByTagName("server"):
			serv.normalize()
			#server and port
			serv.setAttribute("address", self.server)
			serv.setAttribute("port", self.port)
			serv.setAttribute("pass", self.password)
			#nickname
			n = serv.getElementsByTagName("nick")
			if len(n)>0:
				nick = n[0]
				nick.normalize()
				nick.firstChild.data = self._nickname
			#username
			u = serv.getElementsByTagName("username")
			if len(u)>0:
				username = u[0]
				username.normalize()
				nick.firstChild.data = self._username
			#quiet mode
			q = serv.getElementsByTagName("quiet")
			if len(q)>0:
				quietmode = q[0]
				if (self._quietmode == True):
					quietmode.setAttribute("status", "on")
				else:
					quietmode.setAttribute("status", "off")
			#channels
			""" Not set up yet for on-the-fly changing
			for chan in serv.getElementsByTagName("channel"):
				chan.normalize()
				channame = chan.getAttribute("name")
				self.staticchannels[channame] = ChannelProperties()
				notices = chan.getElementsByTagName("notice")
				for notice in notices:
					notice.normalize()
					self.staticchannels[channame].setNotice(notice.firstChild.data.strip())
				logs = chan.getElementsByTagName("log")
				for log in logs:
					if log.getAttribute("on") != "off":
						self.staticchannels[channame].setLog(log.getAttribute("file"))
			"""
		#user access levels
		for user in serv.getElementsByTagName("user"):
			user.normalize()
			n = user.getElementsByTagName("primarynick")[0]
			n.normalize()
			n = n.firstChild.data.strip()
			ui = self.users[n]
			p = user.getElementsByTagName("passwdhash")[0]
			p.normalize()
			p.firstChild.data = ui._password
			""" Not set up yet
			for nick in user.getElementsByTagName("allowednick"):
				nick.normalize()
				ui.addnick(nick.firstChild.data.strip())
			for mask in user.getElementsByTagName("hostmask"):
				mask.normalize()
				ui.addhostmask(mask.firstChild.data.strip())
			for flag in user.getElementsByTagName("flag"):
				flag.normalize()
				ui.setflag(flag.firstChild.data.strip())
			"""
			for lvl in user.getElementsByTagName("accesslevel"):
				lvl.normalize()
				lvl.firstChild.data = ui.accesslevel()
		cf = open(self.configfile, 'w')
		print >>cf, self.doc.toxml()
	
	def on_welcome(self, c, e):
		for chan in self.staticchannels.keys():
			print "Joining "+chan
			c.join(chan)
	
	""" All internal _on_* methods of SingleServerIRCBot should take
		place before the on_* methods here. If you're having trouble
		with things that depend on the internal data, check that.
	"""
	def on_join(self, c, e):
		print "Joined: ", e.source(), e.target(), e.arguments(), str(time.time())
		if irclib.nm_to_n(e.source()) != self._nickname:
			notice = self.staticchannels[e.target()].notice
			if notice != None:
				c.notice(irclib.nm_to_n(e.source()), notice)

	def on_quit(self, c, e):
		nick = irclib.nm_to_n(e.source())
		if nick in self.users:
			self.users[nick].setactive(False)
		print "Quit: ", e.source(), e.target(), e.arguments()
	
	def on_part(self, c, e):
		nick = irclib.nm_to_n(e.source())
		for ch in self.channels:
			if nick in self.channels[ch].users():
				return
		if nick in self.users:
			self.users[nick].setactive(False)
		
	def on_pubmsg(self, c, e):
		print "Received pubmsg"
		a = e.arguments()[0]
		if a[0] == '!':
			command = a[1:]
		else:
			a = e.arguments()[0].split(":", 1)
			if len(a) > 1 and a[0].lower() == self.connection.get_nickname().lower():
				command = a[1].strip()
			else:
				return
		self.do_command(c, irclib.nm_to_n(e.source()), e.target(), command)
	
	def on_action(self, c, e):
		print "Received action from "+e.source()+": "+e.arguments()[0]
	
	def on_privmsg(self, c, e):
		print "Got privmsg from "+irclib.nm_to_n(e.source())+" to "+e.target()
		a = e.arguments()[0]
		if a[0] == '!':
			command = a[1:]
		else:
			a = e.arguments()[0].split(":", 1)
			if len(a) > 1 and a[0].lower() == self.connection.get_nickname().lower():
				command = a[1].strip()
			else:
				command = e.arguments()[0]
		self.do_command(c, irclib.nm_to_n(e.source()), e.target(), command)
	
	def do_command(self, conn, source, target, command):
		print "Executing command "+command
		if command == "":
			return
		self.commandhistory.append((source, command))
		arguments = command.split()[1:]
		command = command.split()[0]
		if target.lower() == self.connection.get_nickname().lower():
			entity = source
			if len(arguments)>0 and arguments[0].startswith('#'):
				channel = arguments[0]
				arguments = arguments[1:]
			else:
				channel = None
		elif self._quietmode:
			entity = source
			channel = target
		else:
			entity = target
			channel = target
		#conn.privmsg(entity, "You sent the command: "+command)
		try:
			lvl = 0
			if source in self.users and self.users[source].isactive():
				lvl = self.users[source].accesslevel()
			if lvl >= self.commands[command][1]:
				(self.commands[command][0])(conn, source, entity, channel, arguments)
			else:
				conn.privmsg(entity, "You don't have the proper access level to do that.")
		except KeyError:
			# if we're in quiet mode, don't respond to an invalid command unless
			# it's repeated three times
			if (self._quietmode):
				count = 0
				for i in xrange(len(self.commandhistory)-1, max(-1, len(self.commandhistory)-50), -1):
					oldcomm = self.commandhistory[i][1].split()
					user = self.commandhistory[i][0]
					if user == target:
						if oldcomm[0] == command:
							count += 1
						else:
							count = 0
							break
				if count > 2:
					self.replyError(conn, source, entity, "ERROR: "+command+" is not a recognized command.")
			else:
				self.replyError(conn, source, entity, "ERROR: "+command+" is not a recognized command.")
		except TypeError, e:
			self.replyError(conn, source, entity, e.args[0])
	
	def replyError(self, c, s, t, m):
		c.privmsg(t, m)
	
	def set_quietmode(self, c, s, t, ch, a):
		if len(a)<1:
			return
		if a[0].startswith('#'):
			a = a[1:]
		if a[0] == "on":
			self._quietmode = True
		elif a[0] == "off":
			self._quietmode = False
		else:
			c.privmsg(t, "Argument '"+a[0]+"' not understood.")
			return
		c.privmsg(t, "Quiet mode "+a[0]+".")
	
	def change_nick(self, c, s, t, ch, a):
		if len(a) < 1:
			c.privmsg(t, "Current nick is "+self._nickname+".")
		c.nick(a[0])
	
	def do_load_module(self, c, s, t, ch, a):
		name = a[0]
		if self._load_one_module(name, {}):
			c.privmsg(t, "Loaded module "+name)
		else:
			c.privmsg(t, "Could not load module "+name)
	
	def do_unload_module(self, c, s, t, ch, a):
		name = a[0]
		if self._unload_module(name):
			c.privmsg(t, "Unloaded module "+name)
		else:
			c.privmsg(t, "Module "+name+" was not loaded to begin with.")

	def do_history(self, c, s, t, ch, a):
		return # security problem, disabling for now
		#send the history to the source, not the channel
		c.privmsg(s, "*** Command history ***")
		for i in xrange(max(-len(self.commandhistory),-20),0):
			c.privmsg(s, "%d: %s" % (-i, self.commandhistory[i][1]))
		c.privmsg(s, "*** End of history ***")
	
	def do_status(self, c, s, t, ch, a):
		c.action(t, "is operating within established parameters.")
		c.privmsg(t, "(Of course, I wouldn't know if I were malfunctioning...)")
		#print self.staticchannels.keys()
		#print self.channels["#defocus"].users()
	
	def do_login(self, c, s, t, ch, a):
		if len(a) < 1:
			c.privmsg(t, "Must specify a password.")
			return
		if s in self.users:
			if self.users[s].checkpassword(a[0]):
				# Just password checking for now, not host checking
				self.users[s].setactive(True)
				c.privmsg(t, "%s successfully logged in." % (s))
			else:
				c.privmsg(t, "Password for %s incorrect." % (s))
		else:
			c.privmsg(t, "%s is not a registered user." % (s))
	
	def do_setpassword(self, c, s, t, ch, a):
		if len(a) < 1:
			c.privmsg(t, "You must choose a non-blank password.")
		if s in self.users:	
			if self.users[s].isactive():
				self.users[s].setpassword(a[0])
				c.privmsg(t, "Password changed.")
			else:
				c.privmsg(t, "Not logged in.")
		else:
			c.privmsg(t, "Not a registered user.")
	
	def do_saveconfig(self, c, s, t, ch, a):
		self._write_config(self.configfile)
		c.privmsg(t, "Configuration saved.")
	
	def do_reloadconfig(self, c, s, t, ch, a):
		self._read_config(self.configfile)
		c.privmsg(t, "Configuration reloaded.")
	
	def send_help(self, c, s, t, ch, a):
		if len(a) == 0:
			c.privmsg(s, "*** Bot help ***")
			c.privmsg(s, "Note: this bot is still under development.")
			c.privmsg(s, "Some features will not work as expected, some")
			c.privmsg(s, "will not work at all, and some will cause global")
			c.privmsg(s, "thermonuclear war. Some features may be available")
			c.privmsg(s, "that aren't listed here.")
			c.privmsg(s, " ")
			c.privmsg(s, "Available commands:")
			for name, mod in self.modules.iteritems():
				if hasattr(mod, "help"):
					for command, info in mod.help.iteritems():
						c.privmsg(s, command.upper())
						c.privmsg(s, "    "+info[0])
			c.privmsg(s, "*** End of help ***")
		else:
			for name, mod in self.modules.iteritems():
				if hasattr(mod, "help") and a[0] in mod.help.keys():
					c.privmsg(t, mod.help[a[0]][1])
					c.privmsg(t, mod.help[a[0]][2])
	
	def do_help(self, c, s, t, ch, a):
		t = threading.Thread(target=self.send_help, args=(c, s, t, ch, a))
		t.start()
		tm = threading.Timer(120, t.join)
			
	def do_quit(self, c, s, t, ch, a):
		self.clean_up()
		c.quit("-")
		time.sleep(2)
		exit(0)
	
	def clean_up(self):
		pass

class ChannelProperties:
	def __init__(self, notice=None, log=None):
		self.notice = notice
		self.log = log
	
	def setNotice(self, notice):
		self.notice = notice
	
	def setLog(self, log):
		self.log = log
		

config = "config/default.xml"
if len(sys.argv) > 1:
	config = sys.argv[1]
bot = SimpleBot(os.getcwd(), config)
bot.start()
