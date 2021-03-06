from aiohttp import web
import aiohttp_jinja2
import jinja2
import asyncio
import websockets

from settings.settings import config, BASE_DIR, UPDATE_DATA_TIME
from routes import setup_routes
from websocket_server import websocket_stream
from system_logger import system_log_process


async def run_shit():
    task = asyncio.create_task(system_log_process(UPDATE_DATA_TIME))
    asyncio.gather(task)

if __name__ == '__main__':
    try:
        ws_server = websocket_stream()
        app = web.Application()
        setup_routes(app)
        aiohttp_jinja2.setup(app,
                             loader=jinja2.FileSystemLoader(
                                 str(BASE_DIR / 'templates')))
        app['config'] = config

        loop = asyncio.get_event_loop()
        loop.run_until_complete(websockets.serve(ws_server.ws_handler, '0.0.0.0', 4000))
        loop.run_until_complete(run_shit())
        loop.run_until_complete(web.run_app(app))
        # надо сделать мягкое закрытие
        loop.run_forever()
    except RuntimeError:
        loop.close()



