
Notes for myself while trying to wrap my head around `asyncio`.

# `get_running_loop`


This fails with `RuntimeError: no running event loop`:

	import asyncio
	asyncio.get_running_loop()

Same:

	import asyncio
	def f():
		return asyncio.get_running_loop()
	f()

Same:

	import asyncio
	def f():
		return asyncio.get_running_loop()
	print(asyncio.run(f()))

This succeeds:

	import asyncio
	async def f():
		return asyncio.get_running_loop()
	print(asyncio.run(f()))

Same:

	import asyncio
	def g():
		return asyncio.get_running_loop()
	async def f():
		return g()
	print(asyncio.run(f()))

# `start_server`

	>>> import asyncio
	>>> asyncio.start_server(print, "", 1234)
	<coroutine object start_server at 0x7261c4b3af80>
	>>> Ctrl-D
	sys:1: RuntimeWarning: coroutine 'start_server' was never awaited
	RuntimeWarning: Enable tracemalloc to get the object allocation traceback


# `asyncio.start_server` and `ssl`

Simplest possible HTTP via `asyncio.start_server`.

	import asyncio

	RESPONSE = """HTTP/1.1 200 OK
	Content-type: text/html

	<!DOCTYPE html>
	<p>Hello, World!
	""".replace("\n", "\r\n").encode("utf-8")

	async def handle(reader, writer):
		writer.write(RESPONSE)

	async def run_server(host, port):
		server = await asyncio.start_server(handle, host=host, port=port)
		async with server:
			await server.serve_forever()

	asyncio.run(run_server("", 1234))

Simplest possible HTTPS via `asyncio.start_server`.

	import asyncio, ssl

	RESPONSE = """HTTP/1.1 200 OK
	Content-type: text/html

	<!DOCTYPE html>
	<p>Hello, World!
	""".replace("\n", "\r\n").encode("utf-8")

	async def handle(reader, writer):
		writer.write(RESPONSE)

	async def run_server(host, port, ssl_context):
		server = await asyncio.start_server(handle, host=host, port=port, ssl=ssl_context)
		async with server:
			await server.serve_forever()

	ssl_context = ssl.SSLContext()
	ssl_context.load_cert_chain(
		"/etc/letsencrypt/live/universefactory.net/cert.pem",
		"/etc/letsencrypt/live/universefactory.net/privkey.pem")
	asyncio.run(run_server("", 1234, ssl_context))


