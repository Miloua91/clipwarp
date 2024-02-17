#!/usr/bin/env python

import asyncio
import websockets
import socket

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

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
    async with websockets.serve(register, "localhost", 5678):
        print(f"server listening on {get_ip_address()}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
