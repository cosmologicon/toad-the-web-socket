
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


