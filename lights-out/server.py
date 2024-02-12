import json
import toad, game

state = game.Gamestate.randomstate(5, 5)

def open_clients():
	for client in toad._clients_by_id.values():
		if client.is_open():
			yield client

def num_clients():
	return len(list(open_clients()))

def send_json(client, method, **kw):
	client.send(json.dumps([method, kw]))

def send_all_json(method, **kw):
	message = json.dumps([method, kw])
	for client in open_clients():
		client.send(message)

def send_debug():
	send_all_json("debug", num_clients = num_clients())

@toad.onopen
def onopen(client):
	send_json(client, "newstate", clientid = client.id, **state.toobj())
	send_debug()

def handle_wantstate(client):
	send_json(client, "newstate", **state.tobj())
def handle_toggle(client, x, y):
	state.toggle(x, y)
	send_all_json("toggle", x = x, y = y, who = client.id)

@toad.onmessage
def onmessage(client, message):
	method, kw = json.loads(message)
	globals()["handle_" + method](client, **kw)
	# TODO: catch and log error

@toad.onerror
def onnerror(client, error):
	print("ERROR", client, error)

@toad.onclose
def onclose(client):
	send_debug()

toad.start_server("", 1234)

