# toad-the-web-socket
A frivolous Python websocket library

**This library is under development and is not ready to be used!** Even when it's ready, you
probably want a better library like [`websockets`](https://pypi.org/project/websockets/). I'm
writing this to be used for making Python games in the PyWeek game jam.

Limitations of this library include but are not limited to:

* The server code only lets you start a single server.
* The client code can only be used to connect to a single server.

## Quick usage: server code

Define callbacks using decorators like `@toad.onconnect`, then run `toad.start_server` with the
host and port to serve from. Use the `client` object passed to the callbacks for interacting with
that client, such as `client.send`.

	import toad

	@toad.onconnect
	def onconnect(client):
		client.send("What is your favorite color?")
	
	@toad.onmessage
	def onmessage(client, message):
		if message.contains("yellow"):
			client.send("Fine. Off you go.")
		elif message.contains("blue"):
			client.kick()

	toad.start_server(host="http://localhost", port=8001)

## Quick usage: client code

Define callbacks using decorators like `@toad.onconnect`, then call `toad.connect_to_server` with
the server URL. To interact with the server, use functions such as `toad.send`.

	import toad

	@toad.onmessage
	def onmessage(message):
		if message == "What is your favorite color?":
			toad.send("blue")
			toad.send("no, yellow!")

	@toad.onkick
	def onkick():
		print("Aaaaaah!")
	
	toad.connect_to_server("http://localhost:8001")

## Callback reference

## `toad.Client`

