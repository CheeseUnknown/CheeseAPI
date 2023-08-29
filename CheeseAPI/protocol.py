import asyncio, http
from typing import TYPE_CHECKING, Dict, Any, Tuple
from multiprocessing import Manager

import httptools
from websockets.legacy.server import HTTPResponse
from websockets.server import WebSocketServerProtocol

from CheeseAPI.app import app
from CheeseAPI.request import Request
from CheeseAPI.signal import signal
from CheeseAPI.utils import async_doFunc

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
        for websocket_beforeConnectionHandle in app.handle.websocket_beforeConnectionHandles:
            await async_doFunc(websocket_beforeConnectionHandle, self.func[1])
        if signal.receiver('websocket_beforeConnectionHandle'):
            await signal.async_send('websocket_beforeConnectionHandle', self.func[1])

        await app.handle._websocket_connectionHandle(self, app)

        while not self.closed:
            try:
                await app.handle._websocket_messageHandle(self, app)
            except:
                ...

        await app.handle._websocket_disconnectionHandle(self, app)
        if signal.receiver('websocket_afterDisconnectionHandle'):
            await signal.async_send('websocket_afterDisconnectionHandle', self.func[1])
        for websocket_afterDisconnectionHandle in app.handle.websocket_afterDisconnectionHandles:
            await async_doFunc(websocket_afterDisconnectionHandle, self.func[1])

    def connection_lost(self, exc: Exception | None) -> None:
        app.websocketWorker.connections.discard(self)
        super().connection_lost(exc)
        if exc is None:
            self.transport.close()

class HttpProtocol(asyncio.Protocol):
    managers: Dict[str, Manager] = {}

    def __init__(self):
        if not HttpProtocol.managers['firstRequest'].value:
            for context_beforeFirstRequestHandle in app.handle.context_beforeFirstRequestHandles:
                context_beforeFirstRequestHandle()
            if signal.receiver('context_beforeFirstRequestHandle'):
                signal.send('context_beforeFirstRequestHandle')
            HttpProtocol.managers['firstRequest'].value = True

        self.transport: asyncio.Transport | None = None
        self.parser = httptools.HttpRequestParser(self)

        self.request: Request = None

    def connection_made(self, transport: asyncio.Transport):
        self.transport = transport

        app.httpWorker.connections.add(self)

    def data_received(self, data: bytes) -> None:
        try:
            self.parser.feed_data(data)
        except httptools.HttpParserUpgrade:
            if self.request.header.get('Upgrade') == 'websocket':
                app.httpWorker.connections.discard(self)
                content = [ self.request.method.value.encode(), b' ', self.request.fullPath.encode(), b' HTTP/1.1\r\n' ]
                for key, value in self.request.header.items():
                    content += [ key.encode(), b': ', value.encode(), b'\r\n' ]
                content.append(b'\r\n')

                self.request.url = self.request.url.replace('http', 'ws')
                self.request.method = None
                self.request.body = None
                self.request.form = None
                self.request.scheme = self.request.scheme.replace('http', 'ws')

                websocketProtocol = WebsocketProtocol()
                websocketProtocol.connection_made(self.transport, self.request)
                websocketProtocol.data_received(b''.join(content))
                self.transport.set_protocol(websocketProtocol)

    def connection_lost(self, exc: Exception | None) -> None:
        app.httpWorker.connections.discard(self)
        if exc is None:
            self.transport.close()

    def on_url(self, url: bytes):
        self.request = Request(('https' if self.transport.get_extra_info('sslcontext') else 'http' + '://') + app.server.host + ':' + str(app.server.port) + url.decode())

        self.request.header['X-Forwarded-For'] = self.transport.get_extra_info('socket').getpeername()[0]

    def on_header(self, name: bytes, value: bytes):
        name = '-'.join([ n.capitalize() for n in name.decode().split('-') ])
        value = value.decode()

        self.request.header[name] = value
        if name == 'Host':
            self.request.url = self.request.url.replace(f'://{app.server.host}:{app.server.port}/', f'://{value}/')

    def on_headers_complete(self):
        self.request.method = http.HTTPMethod(self.parser.get_method().decode())
        if self.parser.should_upgrade():
            return
        if not self.request.header.get('Content-Type'):
            task = asyncio.get_event_loop().create_task(app.handle._httpHandle(self, app))
            task.add_done_callback(app.httpWorker.tasks.discard)
            app.httpWorker.tasks.add(task)

    def on_body(self, body: bytes):
        if self.parser.should_upgrade():
            return
        self.request.body = body

        task = asyncio.get_event_loop().create_task(app.handle._httpHandle(self, app))
        task.add_done_callback(app.httpWorker.tasks.discard)
        app.httpWorker.tasks.add(task)
