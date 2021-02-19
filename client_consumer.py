import asyncio
import logging
import websockets

logging.basicConfig(level=logging.INFO)


def log_message(message: str):
    logging.info(f'message: {message}')


async def consumer_handler(websocket: websockets.WebSocketClientProtocol) -> None:
    async for message in websocket:
        log_message(message)


async def consume(hostname: str, port: int) -> None:
    websocket_resource_url = f'ws://{hostname}:{port}'
    async with websockets.connect(websocket_resource_url) as websocket:
        print('Wait for handle...')
        await consumer_handler(websocket)

async def produce(message: str, host: str, port: int) -> None:
    async with websockets.connect(f'ws://{host}:{port}') as ws:
        await ws.send(message)
        await ws.recv()

if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    loop.run_until_complete(consume(hostname='localhost', port=4000))
    loop.run_forever()


    # asyncio.run(consume('127.0.0.1', 8000))