from typing import Dict

import asyncio

class Websocket:
    def __init__(self):
        self._CLIENTS: Dict[str, asyncio.Queue] = {}

    async def _send(self, message: any, sid: str):
        if sid in self._CLIENTS:
            if isinstance(message, bytes):
                async def func(send):
                    await send({
                        'type': 'websocket.send',
                        'bytes': message
                    })
            else:
                async def func(send):
                    await send({
                        'type': 'websocket.send',
                        'text': str(message)
                    })
            await self._CLIENTS[sid].put(func)

    async def send(self, message: any, sid: str | list[str] | None = None):
        if not sid:
            for key in self._CLIENTS:
                await self._send(message, key)
        elif isinstance(sid, list):
            for s in sid:
                await self._send(message, s)
        else:
            await self._send(message, sid)

    async def _close(self, send):
        await send({
            'type': 'websocket.close'
        })

    async def close(self, sid: str):
        await self._CLIENTS[sid].put(self._close)

    def isOnline(self, sid: str) -> bool:
        return sid in self._CLIENTS

websocket = Websocket()
