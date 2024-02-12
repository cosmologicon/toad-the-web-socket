import random
from functools import cache

def adjs0(w, h, x0, y0):
	for dx, dy in [(0, 0), (-1, 0), (0, -1), (1, 0), (0, 1)]:
		x, y = x0 + dx, y0 + dy
		if 0 <= x < w and 0 <= y < h:
			yield x + w * y
@cache
def adjs(w, h, x0, y0):
	return list(adjs0(w, h, x0, y0))	


class Gamestate:
	def __init__(self, w, h, pattern = None):
		self.w = w
		self.h = h
		if pattern is None:
			self.pattern = [1 for _ in range(w * h)]
		else:
			self.pattern = pattern
	def is_win(self):
		return not any(self.pattern)
	def toggle(self, x0, y0):
		for j in adjs(self.w, self.h, x0, y0):
			self.pattern[j] = 1 - self.pattern[j]
	def toobj(self):
		return { "w": self.w, "h": self.h, "pattern": self.pattern }
	@classmethod
	def fromobj(cls, obj):
		return cls(obj["w"], obj["h"], obj["pattern"])
	@classmethod
	def randomstate(cls, w, h):
		state = cls(w, h)
		for x in range(0, w):
			for y in range(0, h):
				if random.random() < 0.5:
					state.toggle(x, y)
		return state

