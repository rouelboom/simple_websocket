from aiohttp import web
import aiohttp
import asyncio
from system_logger import *

routes = web.RouteTableDef()


def get_value_from_database():
    db_connection = sqlite3.connect('../system-loading.db.sqlite')
    cursor = db_connection.cursor()
    cursor.execute("SELECT cpu FROM sys_log")
    cpu = cursor.fetchall()
    # print(cpu)
    return cpu


@routes.get('/')
async def hello(request):
    data = get_value_from_database()
    image = make_image_by_dots(data)

    return web.Response(text=str(data))
    # return web.FileResponse(path=image)


@routes.get('/ws')
async def websocket_handler(request):

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                await ws.send_str(msg.data + '/answer')
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())

    print('websocket connection closed')

    return ws


@routes.get('/main')
async def test_main(request):
    return web.Response(text="Test text in web")


async def main():
    app = web.Application()
    app.add_routes(routes)

    task1 = asyncio.create_task(web._run_app(app))
    # task2 = asyncio.create_task(system_log_process())
    # await asyncio.gather(task1, task2)
    await asyncio.gather(task1)

if __name__ == '__main__':

    asyncio.run(main())




