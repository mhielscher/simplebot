"""Markov chains"""

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
				print "Possibilities: ", current, " -> ", possible_next
				next = choice(possible_next)
				output.append(next)
				current = tuple(output[-self.n:])
			else:
				break
		
		output_str = self.concatenate(output)
		return output_str
	
	def concatenate(self, source):
		return ' '.join(source)
