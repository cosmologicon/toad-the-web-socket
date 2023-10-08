# Toad the web socket: A frivolous websocket library. By Christopher Night, CC0.
# https://github.com/cosmologicon/toad-the-web-socket

import asyncio
from itertools import count

### CALLBACK SETUP ###

_callbacks = {
	"open": [],
	"message": [],
	"error": [],
	"close": [],
}
def _on(eventname, *args, **kw):
	"""Dispatch the corresponding set of callbacks with the given arguments."""
	ret = None
	for callback in _callbacks[eventname]:
		value = callback(*args, **kw)
		if value is not None:
			ret = value
	return ret
def _callback_decorator_for(eventname):
	"""Create a callback decorator for the given event."""
	def callback_decorator(callback):
		_callbacks[eventname].append(callback)
		return callback
	callback_decorator.__name__ = "on" + eventname
	return callback_decorator

# Callback decorators.
onopen = _callback_decorator_for("open")
onmessage = _callback_decorator_for("message")
onerror = _callback_decorator_for("error")
onclose = _callback_decorator_for("close")


### WEBSOCKET DATA FRAMES ###

# https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers#format

class Frame:
	"""A single data frame."""
	async def build(self, stream_reader):
		raise NotImplementedError

	@staticmethod
	async def read(stream_reader):
		frame = Frame()
		await frame.build(stream_reader)
		return frame

def _join_payload(frames):
	"""Extract the payload from a complete sequence of frames."""
	raise NotImplementedError


### SERVER API ###

class ServerHandler:
	"""Handle a connection to a single client."""
	def __init__(self, stream_reader, stream_writer):
		self.reader = stream_reader
		self.writer = stream_writer
		self.client = Client(self)
		self.callback_obj = self.client
		self.is_open = True

	async def handshake(self):
		raise NotImplementedError
		ret = _on("open", self.client)
		# Allow code to replace the client object by returning from onopen.
		self.callback_obj = ret if ret is not None else self.client

	async def run(self):
		frames = []
		while self.is_open:
			frame = await Frame.read(self.reader)
			if frame.is_close:
				break
			frames.append(frame)
			if not frame.is_final:
				continue
			if not self.is_open:
				break
			message = _join_payload(frames)
			ret = self.onmessage(message)
			if ret is False:
				break
			frames = []

	def onmessage(self, message):
		return _on("message", self.callback_obj, message)

	async def send(self, message):
		if not self.is_open:
			return
		raise NotImplementedError

	async def close(self):
		if not self.is_open:
			return
		self.is_open = False
		raise NotImplementedError
		_on("close", self.callback_obj)


_clients_by_id = {}

class Client:
	_id_generator = count()
	def __init__(self, handler):
		self.handler = handler
		self.id = next(self._id_generator)
		_clients_by_id[self.id] = self

	def is_open(self):
		return self.handler.is_open

	def send(self, message):
		asyncio.run(self.handler.send(message))

	def close(self):
		asyncio.run(self.handler.close())


async def _server_handle(stream_reader, stream_writer):
	"""Called when a new connection is made. Creates a handler and keeps the connection open."""
	handler = ServerHandler(stream_reader, stream_writer)
	await handler.handshake()
	await handler.run()
	await handler.close()

async def _run_server(host, port):
	server = await asyncio.start_server(_server_handle, host=host, port=port)
	async with server:
		await server.serve_forever()

def start_server(host, port, debug = False):
	"""Start serving on the given host and port."""
	asyncio.run(_run_server(host, port), debug=debug)


### CLIENT API ###

def open(url):
	raise NotImplementedError

def send(message):
	raise NotImplementedError

def close():
	raise NotImplementedError

