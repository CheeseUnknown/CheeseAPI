from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from CheeseAPI.request import Request

class WebsocketServer:
    async def subprotocol(self, *, request: 'Request', **kwargs) -> str | None:
        ...

    async def connection(self, *, request: 'Request', **kwargs):
        ...

    async def message(self, *, request: 'Request', message: bytes | str, **kwargs):
        ...

    async def disconnection(self, *, request: 'Request', **kwargs):
        ...

    async def send(self, message: str | bytes):
        ...

    async def close(self, code: int = 1000, reason: str = ''):
        ...
