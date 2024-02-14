import json
import toad, game

GRIDSIZE = 3, 3

state = game.Gamestate.randomstate(*GRIDSIZE)

def send_debug():
	toad.send_all_json(["debug", dict(num_clients = len(toad.open_clients()))])

@toad.onopen
def onopen(client):
	client.send_json(["newstate", dict(clientid = client.id, **state.toobj())])
	send_debug()

def handle_wantstate(client):
	client.send_json(["newstate", dict(**state.toobj())])

def handle_toggle(client, x, y, id):
	if id != state.id or state.is_win():
		client.send_json(["cancelmove", dict(x = x, y = y)])
		return
	state.toggle(x, y)
	toad.send_all_json(["toggle", dict(x = x, y = y, id = state.id, who = client.id)])

def newgame():
	global state
	state = game.Gamestate.randomstate(*GRIDSIZE)
	toad.send_all_json(["newstate", dict(**state.toobj())])

@toad.onmessage
def onmessage(client, message):
	method, kw = json.loads(message)
	globals()["handle_" + method](client, **kw)

@toad.onerror
def onnerror(client, error):
	print("ERROR", client, error)

@toad.onclose
def onclose(client):
	send_debug()

wintimer = 0
pingtimer = 0
@toad.ontick
def ontick():
	global wintimer, pingtimer
	if state.is_win():
		wintimer += 0.5
		if wintimer >= 2:
			newgame()
			wintimer = 0
	else:
		wintimer = 0
	pingtimer += 0.5
	if pingtimer > 5:
		for client in toad.open_clients():
			ping = client.last_ping()
			print(f"PING CLIENT#{client.id}: {ping if ping is None else round(1000 * ping, 1)}ms")
			client.ping()
		pingtimer = 0

toad.start_server("", 1234, tick_seconds=0.5)

