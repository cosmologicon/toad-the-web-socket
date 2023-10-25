# Toad the web socket: A frivolous websocket library. By Christopher Night, CC0.
# https://github.com/cosmologicon/toad-the-web-socket

import asyncio, base64, hashlib
from itertools import count

MAX_EVENT_QUEUE_SIZE = 100
MAX_PAYLOAD_SIZE = 100 << 20  # 100MB, maximum allowed payload size

### EXCEPTION DEFINITIONS ###

class BadClientHandshakeError:
	"""A client connected but failed to send a well-formed WebSocket handshake."""
	def __init__(self, request, client):
		self.request = request
		self.client = client

class PayloadTooLargeError:
	"""A client sent a single message with an indicated payload greater than MAX_PAYLOAD_SIZE."""
	def __init__(self, payload_len):
		self.payload_len = payload_len

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


### HTTP HANDSHAKE HANDLING ###

# https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages#http_requests
async def _read_http_request(stream_reader):
	request_text = await stream_reader.readuntil(b"\r\n\r\n")
	start_line, *lines = request_text.decode("utf-8").split("\r\n")
	# TODO: check start_line
	split_lines = [line.partition(":") for line in lines if line]
	return { key: value.strip() for key, _, value in split_lines }

# Produce the Sec-WebSocket-Accept string for the Server handshake response.
# https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers#server_handshake_response
def _get_accept(key):
	SALT = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
	digest = hashlib.sha1(key.encode("utf-8") + SALT).digest()
	return base64.b64encode(digest).decode("utf-8")

def _get_handshake_response_headers(request):
	if request is None or "Sec-WebSocket-Version" not in request:
		return None
	accept = _get_accept(request["Sec-WebSocket-Key"])
	return [
		("Upgrade", "websocket"),
		("Connection", "Upgrade"),
		("Sec-WebSocket-Accept", accept),
	]

async def _send_http(stream_writer, status_code, status_text, headers = ()):
	lines = [f"HTTP/1.1 {status_code} {status_text}"]
	for key, value in headers:
		lines.append(f"{key}: {value}")
	lines.append("")
	message = "".join(line + "\r\n" for line in lines)
	stream_writer.write(message.encode("utf-8"))
	await stream_writer.drain()


### WEBSOCKET DATA FRAMES ###

# https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers#format

async def _read_int(stream_reader, nbytes):
	return int.from_bytes(await stream_reader.read(nbytes), "big", signed=False)

def _apply_mask(data, mask):
	nreps, extra = divmod(len(data), len(mask))
	mask = mask * nreps + mask[:extra]
	data_int = int.from_bytes(data, "little")
	mask_int = int.from_bytes(mask, "little")
	result_int = data_int ^ mask_int
	return result_int.to_bytes(len(data), "little")	

class Frame:
	"""A single data frame."""
	async def build(self, stream_reader):
		b0, b1 = await stream_reader.read(2)
		assert b0 & 0b01110000 == 0  # RSV = 0
		self.FIN = b0 >> 7
		self.opcode = b0 & 0b00001111
		self.MASK = b1 >> 7
		self.payload_len = b1 & 0b01111111
		if self.payload_len == 126:
			self.payload_len = await _read_int(stream_reader, 2)
		elif self.payload_len == 127:
			self.payload_len = await _read_int(stream_reader, 8)
			if self.payload_len > MAX_PAYLOAD_LENGTH:
				raise PayloadTooLargeError(self.payload_len)
		if self.opcode not in [0, 1, 2, 8]:
			raise NotImplementedError
		self.is_continuation = self.opcode == 0
		self.is_text = self.opcode == 1
		self.is_binary = self.opcode == 2
		self.is_close = self.opcode == 8
		self.is_final = self.FIN == 1
		mask = await stream_reader.read(4)
		self.payload_bytes = await stream_reader.read(self.payload_len)
		if self.MASK:
			self.payload_bytes = _apply_mask(self.payload_bytes, mask)
		else:
			assert not any(mask)

	@staticmethod
	async def read(stream_reader):
		frame = Frame()
		await frame.build(stream_reader)
		return frame

def _join_payload(frames):
	"""Extract the payload from a complete sequence of frames."""
	if len(frames) == 1:
		payload_bytes = frames[0].payload_bytes
	else:
		assert all(frame.is_continuation for frame in frames[1:])
		payload_bytes = b"".join(frame.payload_bytes for frame in frames)
	assert frames[-1].is_final
	assert frames[0].is_text or frames[0].is_binary
	return payload_bytes if frames[0].is_binary else payload_bytes.decode(encoding="utf-8")


### SERVER API ###

class ServerHandler:
	"""Handle a connection to a single client."""
	def __init__(self, stream_reader, stream_writer):
		self.reader = stream_reader
		self.writer = stream_writer
		self.client = Client(self)
		self.callback_obj = self.client
		self.is_open = True
		self.handshake_complete = False

	async def handshake(self):
		request = await _read_http_request(self.reader)
		headers = _get_handshake_response_headers(request)
		if headers is None:
			self.onerror(BadClientHandshakeError(request, self.client))
			await _send_http(self.writer, 400, "Bad Request")
			await self.close()
			return
		await _send_http(self.writer, 101, "Switching Protocols", headers)
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

	def onerror(self, exception):
		return _on("error", self.callback_obj, exception)

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

_id_generator = count()

class Client:
	def __init__(self, handler):
		self.handler = handler
		self.id = next(_id_generator)
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

def start_server(host, port, debug=False, block=False):
	"""Start serving on the given host and port."""
	if block:
		raise NotImplementedError
	asyncio.run(_run_server(host, port), debug=debug)


### CLIENT API ###

def open(url):
	raise NotImplementedError

def send(message):
	raise NotImplementedError

def close():
	raise NotImplementedError

