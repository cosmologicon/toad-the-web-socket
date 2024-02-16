import random
from functools import lru_cache
from itertools import count

def adjs0(w, h, x0, y0):
	for dx, dy in [(0, 0), (-1, 0), (0, -1), (1, 0), (0, 1)]:
		x, y = x0 + dx, y0 + dy
		if 0 <= x < w and 0 <= y < h:
			yield x + w * y
@lru_cache(None)
def adjs(w, h, x0, y0):
	return list(adjs0(w, h, x0, y0))

_id_generator = count()

class Gamestate:
	def __init__(self, w, h, id = None, pattern = None):
		self.w = w
		self.h = h
		if pattern is None:
			self.pattern = [1 for _ in range(w * h)]
		else:
			self.pattern = pattern
		self.id = id if id is not None else next(_id_generator)
	def is_win(self):
		return not any(self.pattern)
	def toggle(self, x0, y0):
		for j in adjs(self.w, self.h, x0, y0):
			self.pattern[j] = 1 - self.pattern[j]
	def toobj(self):
		return { "w": self.w, "h": self.h, "pattern": self.pattern, "id": self.id }
	@classmethod
	def fromobj(cls, obj):
		return cls(obj["w"], obj["h"], obj["id"], obj["pattern"])
	@classmethod
	def randomstate(cls, w, h):
		while True:
			state = cls(w, h)
			for x in range(0, w):
				for y in range(0, h):
					if random.random() < 0.5:
						state.toggle(x, y)
			if not state.is_win():
				return state

