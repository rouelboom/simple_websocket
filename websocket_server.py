import asyncio
import logging
import base64
import json

from websockets import WebSocketServerProtocol
import websockets

from system_logger import make_image_by_dots, get_value_from_database
from settings.settings import UPDATE_DATA_TIME


logging.basicConfig(level=logging.INFO)


class websocket_stream():
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
        while True:
            try:
                data = get_value_from_database()
                img_cpu_bytes = make_image_by_dots(data, 'cpu', 'dynamic')
                img_mem_bytes = make_image_by_dots(data, 'memory', 'dynamic')

                imgs = {}
                imgs['first_image'] = "<img src='data:image/png;base64," + base64.b64encode(
                    img_cpu_bytes.getvalue()).decode() + "'/>"
                imgs['second_image'] = "<img src='data:image/png;base64," + base64.b64encode(img_mem_bytes.getvalue()).decode() + "'/>"
                json_string = json.dumps(imgs)

                await ws.send(json_string)
                await asyncio.sleep(UPDATE_DATA_TIME)

            except websockets.exceptions.ConnectionClosedOK:
                break
