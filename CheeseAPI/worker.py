import asyncio
from typing import TYPE_CHECKING, Set

if TYPE_CHECKING:
    from CheeseAPI.protocol import HttpProtocol

class HttpWorker:
    def __init__(self):
        self.connections: Set['HttpProtocol'] = set()
        self.tasks: Set[asyncio.Task] = set()

class WebsocketWorker:
    def __init__(self):
        self.connections: Set['HttpProtocol'] = set()
        self.tasks: Set[asyncio.Task] = set()
