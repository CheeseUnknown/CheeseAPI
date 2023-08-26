from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from CheeseAPI.request import Request

class WebsocketClient:
    def subprotocolHandle(self, request: 'Request', subprotocols: List[str], **kwargs) -> str | None:
        ...

    async def connectionHandle(self, request: 'Request', **kwargs):
        ...

    async def dataHandle(self, request: 'Request', data: bytes | str, **kwargs):
        ...

    async def disconnectionHandle(self, request: 'Request', **kwargs):
        ...

    async def send(self, value: str | bytes):
        ...

    async def close(self, code: int = 1000, reason: str = ''):
        ...
