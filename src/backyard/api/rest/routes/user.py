from aiohttp import web


def login():
    return web.Response(text='OK')


async def logout():
    return web.Response(text='OK')
