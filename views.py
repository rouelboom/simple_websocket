import aiohttp_jinja2
import base64

from system_logger import make_image_by_dots, get_value_from_database


@aiohttp_jinja2.template('index.html')
async def index(request):
    data = get_value_from_database()

    img_bytes = make_image_by_dots(data, 'cpu', 'static')
    img_tag_cpu = "<img src='data:image/png;base64," + base64.b64encode(
                img_bytes.getvalue()).decode() + "'/>"

    img_bytes = make_image_by_dots(data, 'memory', 'static')
    img_tag_memory = "<img src='data:image/png;base64," + base64.b64encode(
        img_bytes.getvalue()).decode() + "'/>"
    return {'img_cpu': img_tag_cpu, 'img_memory': img_tag_memory}


@aiohttp_jinja2.template('websocket.html')
async def stream_show(request):
    return {}
