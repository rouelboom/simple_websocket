from aiohttp import web
import aiohttp_jinja2
import jinja2

from settings.settings import config, BASE_DIR
from routes import setup_routes

app = web.Application()
setup_routes(app)

aiohttp_jinja2.setup(app,
    loader=jinja2.FileSystemLoader(str(BASE_DIR / 'templates')))
app['config'] = config
web.run_app(app)
