#!/usr/bin/env python

import asyncio
import websockets

CONNECTIONS = set()

async def register(websocket):
    CONNECTIONS.add(websocket)
    
    try:
        async for message in websocket:
            for conn in CONNECTIONS:
                if conn != websocket:
                    await conn.send(message)
                else: print(message)
        await websocket.wait_closed()

    finally:
        CONNECTIONS.remove(websocket)


async def main():
    async with websockets.serve(register, "localhost", 5678):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
