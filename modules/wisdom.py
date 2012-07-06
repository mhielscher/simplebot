#!/usr/bin/python

import random
import threading

class MarkovGenerator:
	def __init__(self, n, mx):
		self.n = n
		self.max = mx
		self.beginnings = list()
		self.ngrams = dict()
		random.seed()
	
	def feed(self, text):
		tokens = self.tokenize(text)
		if len(tokens) < self.n:
			return
		
		beginning = tuple(tokens[:self.n])
		self.beginnings.append(beginning)
		
		for i in xrange(len(tokens) - self.n):
			gram = tuple(tokens[i:i+self.n])
			next = tokens[i+self.n]
			if gram in self.ngrams:
				self.ngrams[gram].append(next)
			else:
				self.ngrams[gram] = [next]
	
	def tokenize(self, text):
		return text.lower().split(' ')
	
	def generate(self):
		from random import choice
		current = choice(self.beginnings)
		output = list(current)
		
		for i in xrange(self.max):
			if current in self.ngrams:
				possible_next = self.ngrams[current]
				next = choice(possible_next)
				output.append(next)
				current = tuple(output[-self.n:])
			else:
				break
		
		output_str = self.concatenate(output)
		return output_str
	
	def concatenate(self, source):
		return ' '.join(source)

autoon = False

mark = MarkovGenerator(2, 20)
f = open('everything.txt', 'r')
for line in f.readlines():
	mark.feed(line)

def speak(c, t):
	c.privmsg(t, mark.generate())

def speak_wisdom(c, s, t, ch, a):
	print ch
	if ch != None:
		t = ch
	speak(c, t)

def nextspeak(c, t):
	global autoon
	if autoon:
		speak(c, t)
		th = threading.Timer(random.randrange(30,180), nextspeak, args=[c, t])
		th.start()

def autospeak(c, s, t, ch, a):
	print ch
	if ch != None:
		t = ch
	global autoon
	autoon = not autoon
	if autoon:
		th = threading.Timer(random.randrange(30,180), nextspeak, args=[c, t])
		th.start()
	

botmodulename = "wisdom"
commands = {
	"speakwisdom" : (speak_wisdom, 0),
	"autospeakwisdom" : (autospeak, 0)
	}
help = {
	"speakwisdom" : ("Speaks a few words of wisdom.", "speakwisdom", "Says something based on log statistics.")
	}
bot = None #this will be set by the bot that loads the module
