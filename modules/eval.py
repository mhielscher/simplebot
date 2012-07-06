#!/usr/bin/python

def do_eval(c, s, t, ch, a):
	if a[0] == 'print':
		a = a[1:]
		m = ' '.join(a)
		print eval(m)
	else:
		m = ' '.join(a)
		eval(m)

botmodulename = "eval"
commands = {
	"eval" : (do_eval, 15),
	}
# Help is disabled so this command stays hidden.
#help = {
#	"eval" : ("Evaluates a Python command.", "eval <command>", "Evaluates <command> in Python: eval('<command>')")
#	}
bot = None #this will be set by the bot that loads the module
