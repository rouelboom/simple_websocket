import asyncio
import logging
import websockets


async def produce(message: str, hostname: str, port: int) -> None:
    async with websockets.connect(f'ws://{hostname}:{port}/ws') as ws:
        await ws.send(message)
        await ws.recv()

if __name__ == '__main__':

    asyncio.run(produce(message='hi mister how are you', hostname='0.0.0.0', port=8080))
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(produce(message='hi', hostname='localhost', port=4000))
