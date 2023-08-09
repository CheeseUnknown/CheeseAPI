from typing import Dict

import asyncio

from CheeseAPI.route import matchPath

class Websocket:
    def __init__(self):
        self._CLIENTS: Dict[str, Dict[str, asyncio.Queue]] = {}

    async def _send(self, message: any, path: str, sid: str):
        if path in self._CLIENTS and sid in self._CLIENTS[path]:
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
            await self._CLIENTS[path][sid].put(func)

    async def send(self, message: any, path: str, sid: str | list[str] | None = None):
        if path in self._CLIENTS:
            if not sid:
                for key in self._CLIENTS[path]:
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

    async def close(self, path: str, sid: str | list[str] | None = None):
        if path in self._CLIENTS:
            if not sid:
                for key in self._CLIENTS[path]:
                    await self._CLIENTS[path][key].put(self._close)
            elif isinstance(sid, list):
                for s in sid:
                    await self._CLIENTS[path][s].put(self._close)
            else:
                await self._CLIENTS[path][sid].put(self._close)

websocket = Websocket()
