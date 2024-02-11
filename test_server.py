"""
To use, run and then in a web browser console:
socket = new WebSocket("ws://localhost:1234")
socket.addEventListener('message', (event) => console.log('Message from server: ' + event.data))
socket.send("Hello world.")
"""


import toad

@toad.onopen
def onopen(client):
	print("open", client)

@toad.onmessage
def onmessage(client, message):
	print("message", client, message)
	client.send(f"You said: {message}")

toad.start_server("", 1234)

