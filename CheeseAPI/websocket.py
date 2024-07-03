from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from CheeseAPI.request import Request

class WebsocketServer:
    def __init__(self):
        self.open_timeout: float | None = 10
        self.ping_interval: float | None = 20
        self.ping_timeout: float | None = 20
        self.close_timeout: float | None = None
        self.max_size: int | None = 2**20
        self.max_queue: int | None = 2**5
        self.read_limit: int = 2**16
        self.write_limit: int = 2**16

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
