#!/usr/bin/env python

import asyncio
import websockets

CONNECTIONS = {}

async def register(websocket):
    name = f'Client_{len(CONNECTIONS) + 1}'
    CONNECTIONS[name] = websocket
    print(f"{name} connected")
    try:
        async for message in websocket:
            for conn_name, conn in CONNECTIONS.items():
                if conn != websocket:
                    await conn.send(message)
                else:
                    print(f"Message received from {conn_name}: {message}")
        await websocket.wait_closed()

    finally:
        del CONNECTIONS[name]
        print(f"{name} disconnected")


async def main():
    print("listening...")
    async with websockets.serve(register, "localhost", 5678):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
