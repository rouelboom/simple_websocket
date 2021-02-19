from aiohttp import web
import aiohttp_jinja2
import sqlite3
import base64

from system_logger import make_image_by_dots


def get_value_from_database():
    db_connection = sqlite3.connect('system-loading.db.sqlite')
    cursor = db_connection.cursor()
    cursor.execute("SELECT cpu FROM sys_log")
    cpu = cursor.fetchall()
    # print(cpu)
    return cpu

#
# @aiohttp_jinja2.template('index.html')
# async def index(request):
#     data = get_value_from_database()
#     img_bytes = make_image_by_dots(data)
#     content = img_bytes.getvalue()
#     print(f'cpu:len {len(data)}')
#     return {'cpu_stats': data, 'img': content}
#     # return web.Response(body=content, content_type='image/png')

@aiohttp_jinja2.template('index.html')
async def index(request):
    data = get_value_from_database()
    img_bytes = make_image_by_dots(data)
    img_tag = "<img src='data:image/png;base64," + base64.b64encode(img_bytes.getvalue()).decode() + "'/>"
    return {'img': img_tag}

    # return web.Response(body=img_tag, content_type='text/html')

async def stream_show(request):
    return web.Response(text='Hello')
