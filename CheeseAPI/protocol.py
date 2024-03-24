import http
from typing import TYPE_CHECKING, Dict, Any, Tuple

import asyncio, httptools
from websockets.server import WebSocketServerProtocol

from CheeseAPI.request import Request
from CheeseAPI.app import app

if TYPE_CHECKING:
    from CheeseAPI.response import BaseResponse
    from CheeseAPI.websocket import WebsocketServer

class HttpProtocol(asyncio.Protocol):
    def __init__(self):
        self.transport: asyncio.Transport | None = None
        self.parser = httptools.HttpRequestParser(self)
        self.request: Request | None = None
        self.response: 'BaseResponse' | None = None
        self.kwargs: Dict[str, Any] = {}

    def connection_made(self, transport: asyncio.Transport):
        self.transport = transport

    def data_received(self, data: bytes) -> None:
        self.request = None
        self.response = None
        self.kwargs = {}

        try:
            self.parser.feed_data(data)

            if self.request.body:
                self.request._parseBody()

            asyncio.get_event_loop().create_task(app._handle.http(self))
        except httptools.HttpParserUpgrade:
            self.request._upgrade()

            websocketProtocol = WebsocketProtocol(self)
            websocketProtocol.connection_made(self.transport)
            websocketProtocol.data_received(data)
            self.transport.set_protocol(websocketProtocol)

    def on_url(self, url: bytes):
        self.request = Request(http.HTTPMethod(self.parser.get_method().decode()), url.decode())

    def on_header(self, key: bytes, value: bytes):
        self.request.headers['-'.join([t.capitalize() for t in key.decode().split('-')])] = value.decode()

    def on_headers_complete(self):
        self.request.client = self.request.headers.get('X-Real-Ip', None)
        self.request.origin = self.request.headers.get('Origin', None)
        self.request.scheme = self.request.headers.get('X-Forwarded-Proto', None)

    def on_body(self, body: bytes):
        if self.request.body is None:
            self.request.body = b''
        self.request.body += body

    def connection_lost(self, exc: Exception | None):
        self.transport.close()

class WebsocketProtocol(WebSocketServerProtocol):
    def __init__(self, httpProcotol: HttpProtocol):
        self.transport: asyncio.Transport = httpProcotol.transport
        self.server: 'WebsocketServer' | None = None
        self.request: Request = httpProcotol.request
        self.response: 'BaseResponse' | None = None
        self.kwargs: Dict[str, Any] = httpProcotol.kwargs

        super().__init__(
            ws_handler = self.ws_handle,
            ws_server = FakeWebsocketServer()
        )

    async def process_request(self, *args, **kwargs) -> Tuple[int, Dict[str, str], bytes] | None:
        results = await app._handle.websocket_request(self)
        if results:
            return results

        self.server.send = self._send
        self.server.close = self._close

    def process_subprotocol(self, *args, **kwargs) -> str | None:
        return self.request.subprotocol

    async def ws_handle(self, *args, **kwargs):
        await app._handle.websocket(self)

    def connection_lost(self, exc: Exception | None):
        self.transport.close()
        super().connection_lost(exc)

    async def _send(self, message: str | bytes):
        await app._handle.websocket_send(self, message)

    async def _close(self, code: int = 1000, reason: str = ''):
        await app._handle.websocket_close(self, code, reason)

class FakeWebsocketServer:
    closing = False

    def register(self, *args, **kwargs) -> None:
        ...

    def unregister(self, *args, **kwargs) -> None:
        ...

    def is_serving(self) -> bool:
        return not self.closing
