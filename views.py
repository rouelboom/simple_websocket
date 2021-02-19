from aiohttp import web
import aiohttp_jinja2
import sqlite3

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
    content = img_bytes.getvalue()
    print(f'cpu:len {len(data)}')
    # return {'cpu_stats': data, 'img': path_to_img}
    return web.Response(body=content, content_type='image/png')


#
# @router.get("/{post}/image")
# async def render_post_image(request: web.Request) -> web.Response:
#     post_id = request.match_info["post"]
#     db = request.config_dict["DB"]
#     async with db.execute("SELECT image FROM posts WHERE id = ?", [post_id]) as cursor:
#         row = await cursor.fetchone()
#         if row is None or row["image"] is None:
#             img = PIL.Image.new("RGB", (64, 64), color=0)
#             fp = io.BytesIO()
#             img.save(fp, format="JPEG")
#             content = fp.getvalue()
#         else:
#             content = row["image"]
#     return web.Response(body=content, content_type="image/jpeg")