from aiohttp import web
import aiohttp
import aiohttp_jinja2
import sqlite3
import base64
import websockets

from system_logger import make_image_by_dots


def get_value_from_database():
    db_connection = sqlite3.connect('system-loading.db.sqlite')
    cursor = db_connection.cursor()
    cursor.execute("SELECT cpu FROM sys_log")
    cpu = cursor.fetchall()
    # print(cpu)
    return cpu

@aiohttp_jinja2.template('index.html')
async def index(request):
    data = get_value_from_database()
    img_bytes = make_image_by_dots(data)
    img_tag = "<img src='data:image/png;base64," + base64.b64encode(
                img_bytes.getvalue()).decode() + "'/>"
    return {'img': img_tag}



@aiohttp_jinja2.template('websocket.html')
async def stream_show(request):
    data = get_value_from_database()
    img_bytes = make_image_by_dots(data)
    img_tag = "<img src='data:image/png;base64," + base64.b64encode(
                img_bytes.getvalue()).decode() + "'/>"
    return {'img': img_tag}


# async def websocket_handler(request):
#
#     ws = web.WebSocketResponse()
#     await ws.prepare(request)
#
#     async for msg in ws:
#         if msg.type == aiohttp.WSMsgType.TEXT:
#             if msg.data == 'close':
#                 await ws.close()
#             else:
#                 await ws.send_str(msg.data + '/answer')
#         elif msg.type == aiohttp.WSMsgType.ERROR:
#             print('ws connection closed with exception %s' %
#                   ws.exception())
#
#     print('websocket connection closed')
#
#     return ws