import asyncio
import logging
import base64

import websockets
import aiohttp
from aiohttp import web
from websockets import WebSocketServerProtocol

from system_logger import make_image_by_dots, get_value_from_database


logging.basicConfig(level=logging.INFO)



class my_websocket_server():
    clients = set()

    async def register(self, ws: WebSocketServerProtocol) -> None:
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol) -> None:
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str) -> None:
        if self.clients:
            await asyncio.wait([client.send(message) for client in self.clients])

    async def ws_handler(self, ws: WebSocketServerProtocol, url: str) -> None:
        await self.register(ws)
        try:
            await self.distribute(ws)
        finally:
            await self.unregister(ws)

    async def distribute(self, ws: WebSocketServerProtocol) -> None:
        async for message in ws:
            print(message)
            counter = 1
            # это не красиво, но пока по другому не придумал
            while True:
                data = get_value_from_database()
                img_bytes = make_image_by_dots(data)

                dots = []
                for i in range(counter):
                    dots.append(i)
                img_tag = "<img src='data:image/png;base64," + base64.b64encode(
                            img_bytes.getvalue()).decode() + "'/>"
                counter += 1

                await ws.send(img_tag)
                await asyncio.sleep(1)


# if __name__ == '__main__':
#     server = my_websocket_server()
#     start_server = websockets.serve(server.ws_handler, '0.0.0.0', 4000)
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(start_server)
#     loop.run_forever()
