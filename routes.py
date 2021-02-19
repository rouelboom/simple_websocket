from views import index, stream_show

def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_get('/ws', stream_show)

