# toad-the-web-socket
A frivolous Python websocket library

**This library is under development and is not ready to be used!** Even when it's ready, you
probably want a better library like [`websockets`](https://pypi.org/project/websockets/).

## Quick usage: server code (asynchronous version)

	import toad

	@toad.onopen
	def onopen(client):
		client.send("What is your favorite color?")

	@toad.onmessage
	def onmessage(client, message):
		if message.contains("yellow"):
			client.send("Fine. Off you go.")
		elif message.contains("blue"):
			client.close()

	toad.start_server(host="http://localhost", port=8001)

## Quick usage: server code (synchronous version)

	import toad

	toad.start_server(host="http://localhost", port=8001, block=False)

	while True:
		for client in toad.opens():
			client.send("What is your favorite color?")
		for client, message in toad.messages():
			if message.contains("yellow"):
				client.send("Fine. Off you go.")
			elif message.contains("blue"):
				client.close()

## Quick usage: client code (asynchronous version)

	import toad

	@toad.onmessage
	def onmessage(message):
		if message == "What is your favorite color?":
			toad.send("blue")
			toad.send("no, yellow!")

	@toad.onclose
	def onclose():
		print("Aaaaaah!")

	toad.open("http://localhost:8001")

## Quick usage: client code (synchronous version)

	import toad

	toad.open("http://localhost:8001", block=False)

	while toad.isopen():
		for message in toad.messages():
			if message == "What is your favorite color?":
				toad.send("blue")
				toad.send("no, yellow!")
	print("Aaaaaah!")

## To install

Download `toad.py` and put it in your source directory. To install from command line:

	curl https://raw.githubusercontent.com/cosmologicon/toad-the-web-socket/master/toad.py > my-source-directory/toad.py

## Usage warning

I'm writing this to be used for Python games in the PyWeek game jam. It's designed to handle the
simple case of a Python game server. The API is based on the JavaScript WebSocket API, to
facilitate porting client code from Python to JavaScript.

Limitations of this library include but are not limited to:

* No sophisticated error handling.
* You can't start both a server and a client in the same program.
* The server code only lets you start a single server.
* No way to stop a server once it's started.
* The client code can only be used to connect to a single server.

## Server API

	toad.start_server(host: str, port: int, block=True)

If `block` is `True`, then the call will block until `toad.stop_server` is called.

	toad.stop_server()

### Server callbacks

By default, `client` is a `toad.Client` object in server callbacks, although this can be overridden
(see `toad.Client` below).

	@toad.onopen
	def onopen(client):

	@toad.onmessage
	def onmessage(client, message):

`message` is either be `str` or `bytes`, depending on which websocket message type was used.
Normally there's no point returning anything from this callback. If you return `False` then the
connection will be closed, as if you had called `client.close()`.

	@toad.onerror
	def onerror(client, exception):
	
	@toad.onclose
	def onclose(client):

You can define multiple callbacks with the same decorator. That's fine. They'll all be executed in
the order they were added.

### `toad.Client`

The server has one `toad.Client` object per active connection.

`toad.Client.id`: a unique identifier.

`toad.Client.send(message)`: send a message to the client.

`toad.Client.close()`: close the connection to the client.

Tip: you can replace the client object that gets passed to callbacks with your own object. To do
this, return a value from the `onopen` callback. This will then be passed to subsequent callbacks
such as `onmessage` for this client.

	import toad
	import random

	class Player:
		def __init__(self, client, team):
			self.client = client
			self.team = team

	@toad.onopen
	def onopen(client):
		team = random.choice(["red", "blue"])
		client.send(f"Welcome to team {team}")
		return Player(client, team)  # Return an object to replace the client object.
	
	@toad.onmessage
	def onmessage(player, message):  # Replaced object is passed to subsequent callbacks.
		print(f"Message from team {player.team}: {message}")

	toad.start_server(host="http://localhost", port=8001)

## Client API

There's no server object: the client code just calls methods of `toad` directly.

	toad.open(url: str, block=True)

If `block` is `True`, then the call will block until the connection is closed, by either the client
or the server.

	toad.isopen()

	toad.send(message)

	toad.close()

### Client callbacks

	@toad.onopen
	def onopen():

	@toad.onmessage
	def onmessage(message):
	
	@toad.onerror
	def onerror(exception):
	
	@toad.onclose
	def onclose():

