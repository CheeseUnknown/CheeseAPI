from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from CheeseAPI.request import Request

class WebsocketServer:
    def __init__(self, *, open_timeout: float | None = 10, ping_interval: float | None = 20, ping_timeout: float | None = 20, close_timeout: float | None = None, max_size: float | None = 2**20, max_queue: int | None = 2**5, read_limit: int = 2**16, write_limit: int = 2**16):
        self.open_timeout: float | None = open_timeout
        self.ping_interval: float | None = ping_interval
        self.ping_timeout: float | None = ping_timeout
        self.close_timeout: float | None = close_timeout
        self.max_size: int | None = max_size
        self.max_queue: int | None = max_queue
        self.read_limit: int = read_limit
        self.write_limit: int = write_limit

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
