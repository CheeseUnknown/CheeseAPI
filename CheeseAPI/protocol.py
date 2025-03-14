from typing import TYPE_CHECKING, Dict, Any, Tuple
from http import HTTPMethod
from asyncio import get_event_loop, Protocol, Transport

from websockets.server import WebSocketServerProtocol
from httptools import HttpRequestParser, HttpParserUpgrade

from CheeseAPI.request import Request
from CheeseAPI.app import app

if TYPE_CHECKING:
    from CheeseAPI.response import BaseResponse
    from CheeseAPI.websocket import WebsocketServer

class HttpProtocol(Protocol):
    def __init__(self):
        self.transport: Transport | None = None
        self.parser = HttpRequestParser(self)
        self.request: Request | None = None
        self.response: 'BaseResponse' | None = None
        self.kwargs: Dict[str, Any] = {}

    def connection_made(self, transport: Transport):
        self.transport = transport

    def data_received(self, data: bytes) -> None:
        try:
            self.parser.feed_data(data)
        except HttpParserUpgrade:
            self.request._upgrade()

            websocketProtocol = WebsocketProtocol(self)
            websocketProtocol.connection_made(self.transport)
            websocketProtocol.data_received(data)
            self.transport.set_protocol(websocketProtocol)

    def on_url(self, url: bytes):
        url = url.decode()
        try:
            self.request = Request(HTTPMethod(self.parser.get_method().decode()), url)
        except ValueError:
            self.request = Request(None, url)
        self.response = None
        self.kwargs = {}

    def on_header(self, key: bytes, value: bytes):
        self.request.headers['-'.join([t.capitalize() for t in key.decode().split('-')])] = value.decode()

    def on_headers_complete(self):
        self.request._client = self.request.headers.get('X-Real-Ip', self.transport.get_extra_info('socket').getpeername()[0])
        self.request._origin = self.request.headers.get('Origin', f'{self.transport.get_extra_info("socket").getsockname()[0]}:{self.transport.get_extra_info("socket").getsockname()[1]}')
        self.request._scheme = self.request.headers.get('X-Forwarded-Proto', 'https' if self.transport.get_extra_info('sslcontext') else 'http')

        if 'Cookie' in self.request.headers:
            self.request._cookie = {
                t.split('=')[0]: t.split('=')[1] for t in self.request.headers['Cookie'].split('; ')
            }

    def on_body(self, body: bytes):
        if self.request.body is None:
            self.request._body = b''
        self.request._body += body

    def on_message_complete(self):
        if not self.parser.should_upgrade():
            self.request._parseBody()
            get_event_loop().create_task(app._handle.http(self))

    def connection_lost(self, exc: Exception | None):
        self.transport.close()

class WebsocketProtocol(WebSocketServerProtocol):
    def __init__(self, httpProcotol: HttpProtocol):
        self.transport: Transport = httpProcotol.transport
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

        self.open_timeout = self.server.open_timeout
        self.ping_interval = self.server.ping_interval
        self.ping_timeout = self.server.ping_timeout
        self.close_timeout = self.server.close_timeout
        self.max_size = self.server.max_size
        self.max_queue = self.server.max_queue
        self.read_limit = self.server.read_limit
        self.write_limit = self.server.write_limit

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
