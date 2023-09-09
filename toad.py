# Toad the web socket: A frivolous websocket library. By Christopher Night, CC0.
# https://github.com/cosmologicon/toad-the-web-socket


# Callback setup

_callbacks = {
	"open": [],
	"message": [],
	"error": [],
	"close": [],
}
def _on(eventname, *args, **kw):
	ret = None
	for callback in _callbacks[eventname]:
		value = callback(*args, **kw)
		if value is not None:
			ret = value
	return ret
def _callback_decorator_for(eventname):
	def callback_decorator(callback):
		_callbacks[eventname].append(callback)
		return callback
	callback_decorator.__name__ = "on" + eventname
	return callback_decorator
onopen = _callback_decorator_for("open")
onmessage = _callback_decorator_for("message")
onerror = _callback_decorator_for("error")
onclose = _callback_decorator_for("close")

# Server API

def start_server(host, port):
	raise NotImplementedError

class Client:
	def __init__(self):
		raise NotImplementedError
	
	def send(self, message):
		raise NotImplementedError
	
	def close(self):
		raise NotImplementedError


# Client API

def open(url):
	raise NotImplementedError

def send(message):
	raise NotImplementedError

def close():
	raise NotImplementedError

