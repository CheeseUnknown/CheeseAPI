import asyncio, http, traceback
from typing import TYPE_CHECKING, Dict, Any, Tuple, Deque, Self
from multiprocessing import Manager
from collections import deque

import httptools
from CheeseLog import logger
from websockets.legacy.server import HTTPResponse
from websockets.server import WebSocketServerProtocol

from CheeseAPI.app import app
from CheeseAPI.request import Request
from CheeseAPI.signal import signal

if TYPE_CHECKING:
    from CheeseAPI.websocket import WebsocketClient

class FakeWebsocketServer:
    closing = False

    def register(self, *args, **kwargs) -> None:
        ...

    def unregister(self, *args, **kwargs) -> None:
        ...

    def is_serving(self) -> bool:
        return not self.closing

class WebsocketProtocol(WebSocketServerProtocol):
    def __init__(self):
        self.transport: asyncio.Transport | None = None

        self.request: Request | None = None
        self.func: Tuple['WebsocketClient', Dict[str, Any]] | None = None

        super().__init__(
            ws_handler = self.ws_handler,
            ws_server = FakeWebsocketServer()
        )

    def connection_made(self, transport, request):
        self.transport = transport
        self.request = request

        app.websocketWorker.connections.add(self)

        super().connection_made(transport)

    async def process_request(self, *args, **kwargs) -> HTTPResponse | None:
        result = await app.handle._websocket_requestHandle(self, app)
        if len(result) == 3:
            return result
        self.func = result
        self.func[0].send = self.send
        self.func[0].close = self.close

    def process_subprotocol(self, *args, **kwargs) -> str:
        self.func[1]['subprotocol'] = app.handle._websocket_subprotocolHandle(self, app)
        return self.func[1]['subprotocol']

    async def ws_handler(self, *args, **kwargs):
        await app.handle._websocket_handler(self, app)

    def connection_lost(self, exc: Exception | None) -> None:
        app.websocketWorker.connections.discard(self)
        super().connection_lost(exc)
        if exc is None:
            self.transport.close()

        app.handle._websocket_disconnectionHandle(self, app)

class Protocol:
    def __init__(self, parser):
        self.transport: asyncio.Transport | None = None
        self.parser = parser

        self.request: Request = None

        self.deque: Deque[Self] = deque()
        self.task = None
        self.timeoutTask = None

class HttpProtocol(asyncio.Protocol):
    managers: Dict[str, Manager] = {}

    def __init__(self):
        if not HttpProtocol.managers['firstRequest'].value:
            for context_beforeFirstRequestHandle in app.handle.context_beforeFirstRequestHandles:
                context_beforeFirstRequestHandle()
            if signal.receiver('context_beforeFirstRequestHandle'):
                signal.send('context_beforeFirstRequestHandle')
            HttpProtocol.managers['firstRequest'].value = True

        self.protocol: Protocol = Protocol(httptools.HttpRequestParser(self))

    def connection_made(self, transport: asyncio.Transport):
        self.protocol.transport = transport

        app.httpWorker.connections.add(self)

    def data_received(self, data: bytes) -> None:
        try:
            self.protocol.parser.feed_data(data)
        except httptools.HttpParserUpgrade:
            if self.protocol.request.headers.get('Upgrade') == 'websocket':
                app.httpWorker.connections.discard(self)
                content = [ self.protocol.request.method.value.encode(), b' ', self.protocol.request.fullPath.encode(), b' HTTP/1.1\r\n' ]
                for key, value in self.protocol.request.headers.items():
                    content += [ key.encode(), b': ', value.encode(), b'\r\n' ]
                content.append(b'\r\n')

                self.protocol.request.url = self.protocol.request.url.replace('http', 'ws')
                self.protocol.request.method = None
                self.protocol.request.body = None
                self.protocol.request.form = None
                self.protocol.request.scheme = self.protocol.request.scheme.replace('http', 'ws')

                websocketProtocol = WebsocketProtocol()
                websocketProtocol.connection_made(self.protocol.transport, self.protocol.request)
                websocketProtocol.data_received(b''.join(content))
                self.protocol.transport.set_protocol(websocketProtocol)

    def connection_lost(self, exc: Exception | None) -> None:
        app.httpWorker.connections.discard(self)
        if exc is None:
            self.protocol.transport.close()
            if self.protocol.timeoutTask:
                self.protocol.timeoutTask.cancel()
                self.protocol.timeoutTask = None

    def on_url(self, url: bytes):
        self.protocol.request = Request(('https' if self.protocol.transport.get_extra_info('sslcontext') else 'http' + '://') + app.server.host + ':' + str(app.server.port) + url.decode())

        self.protocol.request.headers['X-Forwarded-For'] = self.protocol.transport.get_extra_info('socket').getpeername()[0]

    def on_header(self, name: bytes, value: bytes):
        name = '-'.join([ n.capitalize() for n in name.decode().split('-') ])
        value = value.decode()

        self.protocol.request.headers[name] = value
        if name == 'Host':
            self.protocol.request.url = self.protocol.request.url.replace(f'://{app.server.host}:{app.server.port}/', f'://{value}/')

    def on_headers_complete(self):
        self.protocol.request.method = http.HTTPMethod(self.protocol.parser.get_method().decode())
        if self.protocol.parser.should_upgrade():
            return

        if not self.protocol.request.headers.get('Content-Type'):
            self.protocol.transport.pause_reading()
            if self.protocol.task:
                self.protocol.transport.pause_reading()
                self.protocol.deque.append(self.protocol)
            else:
                self.protocol.task = asyncio.get_event_loop().create_task(app.handle._httpHandle(self.protocol, app))
                self.protocol.task.add_done_callback(app.httpWorker.tasks.discard)
                app.httpWorker.tasks.add(self.protocol.task)

    def on_body(self, body: bytes):
        if self.protocol.parser.should_upgrade():
            return
        if self.protocol.request.body is None:
            self.protocol.request.body = b''
        self.protocol.request.body += body

        if len(self.protocol.request.body) == int(self.protocol.request.headers['Content-Length']):
            self.protocol.request.parseBody()
            self.protocol.transport.pause_reading()
            if self.protocol.task:
                self.protocol.transport.pause_reading()
                self.protocol.deque.append(self.protocol)
            else:
                self.protocol.task = asyncio.get_event_loop().create_task(app.handle._httpHandle(self.protocol, app))
                self.protocol.task.add_done_callback(app.httpWorker.tasks.discard)
                app.httpWorker.tasks.add(self.protocol.task)
