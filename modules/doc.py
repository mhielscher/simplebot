#!/usr/bin/python

def do_doc(c, s, t, ch, a):
	f = open("output-dbg.xml", 'w')
	print >>f, bot.doc.toxml()

botmodulename = "doc"
commands = {
	"printdoc" : (do_doc, 15)
	}
help = {
	"printdoc" : ("debug", "printdoc", "debug")
	}
bot = None #this will be set by the bot that loads the module
