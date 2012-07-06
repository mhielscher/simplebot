import hashlib

class UserInfo:
	def __init__(self, n, p, h=None a=0):
		self._primarynick
		self._allowednicks = []
		self._hostmasks = []
		if h != None:
			self._hostmasks.append(h)
		self._flags = {}
		d = hashlib.sha256()
		d.update(p)
		self._password = d.hexdigest()
		self._access_level = a
	
	def primarynick(self):
		return _primarynick
	
	def allowednicks(self):
		return _allowednicks
	
	def is_allowednick(self, n):
		return n in _allowednicks
	
	def addnick(self, n):
		_allowednicks.append(n)
	
	def hostmasks(self):
		return _hostmasks
	
	def is_hostmask(self, h):
		return h in _hostmasks
	
	def addhostmask(self, h):
		_hostmasks.append(h)
	
	def flags(self):
		return _flags
	
	def setflag(self, flag):
		_flags[flag] = 1
	
	def unsetflag(self, flag):
		del _flags[flag]
	
	def checkpassword(self, p):
		d = hashlib.sha256()
		d.update(p)
		return self._password == d.hexdigest()
	
	

"""
access level
nick
hostmask(s)
flags (autoident, autoop, banprotect, isabot, swearexempt, etc.)
memos
password (md5sum/hashlib or sha256)
"""
#by default, hostmasks and nicks are only used for autoident
# you can ident any time with your password
# unless you set the restrictident flag
# then you have to match a nick and hostmask before ident'ing with passwd
