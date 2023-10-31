import os, time, http, traceback, asyncio
from typing import TYPE_CHECKING, List, Callable, Tuple, Dict, Any

import websockets
from CheeseLog import logger, ProgressBar
from websockets.legacy.server import HTTPResponse

from CheeseAPI.route import paths
from CheeseAPI.response import FileResponse, BaseResponse, Response
from CheeseAPI.signal import signal
from CheeseAPI.module import Module, LocalModule

if TYPE_CHECKING:
    from CheeseAPI.app import App
    from CheeseAPI.protocol import WebsocketProtocol, Protocol

class Handle:
    def __init__(self):
        self.server_beforeStartingHandles: List[Callable] = []
        self.worker_beforeStartingHandles: List[Callable] = []
        self.worker_afterStartingHandles: List[Callable] = []
        self.server_afterStartingHandles: List[Callable] = []
        self.context_beforeFirstRequestHandles: List[Callable] = []
        self.http_beforeRequestHandles: List[Callable] = []
        self.http_afterResponseHandles: List[Callable] = []
        self.websocket_beforeConnectionHandles: List[Callable] = []
        self.websocket_afterDisconnectionHandles: List[Callable] = []
        self.worker_beforeStoppingHandles: List[Callable] = []
        self.server_beforeStoppingHandles: List[Callable] = []

    async def _httpHandle(self, protocol: 'Protocol', app: 'App'):
        try:
            if app.server.static and protocol.request.path.startswith(app.server.static):
                if await self._http_responseHandle(protocol, app, await self._http_staticHandle(protocol, app)):
                    return

            funcs = paths.match(protocol.request.path)

            if not funcs:
                if await self._http_responseHandle(protocol, app, await self._http_404Handle(protocol, app)):
                    return

            if protocol.request.method not in funcs:
                if protocol.request.method == http.HTTPMethod.OPTIONS and (app.cors.origin == '*' or protocol.request.method in app.cors.origin):
                    if await self._http_responseHandle(protocol, app, await self._http_optionsHandle(protocol, app)):
                        return
                elif await self._http_responseHandle(protocol, app, await self._http_405Handle(protocol, app)):
                    return

            for http_beforeRequestHandle in self.http_beforeRequestHandles:
                await http_beforeRequestHandle(**{ 'request': protocol.request })
            if signal.receiver('http_beforeRequestHandle'):
                await signal.async_send('http_beforeRequestHandle', { 'request': protocol.request })

            func = funcs[protocol.request.method][0]
            kwargs = funcs[protocol.request.method][1]
            kwargs['request'] = protocol.request
            response = await func(**kwargs)
            if await self._http_responseHandle(protocol, app, response):
                return

            await self._http_responseHandle(protocol, app, await self._http_noResponseHandle(protocol, app))
        except BaseException as e:
            await self._http_responseHandle(protocol, app, await self._http_500Handle(protocol, app, e))

    def _exitSignalHandle(self, server):
        server.close()

    def server_beforeStartingHandle(self, func: Callable):
        self.server_beforeStartingHandles.append(func)

    def _server_beforeStartingHandle(self):
        from CheeseAPI.app import app

        app.g['timer'] = time.time()

        logger.starting(f'The master process {os.getpid()} started', f'The master process <blue>{os.getpid()}</blue> started')

        logger.starting(f'''Workspace information:
CheeseAPI: {app.workspace.CheeseAPI}
Base: {app.workspace.base}''' + (f'''
Static: {app.workspace.static}''' if app.server.static else '') + (f'''
Log: {app.workspace.log}''' if app.workspace.logger else '') + (f'''
Logger: {app.workspace.logger}''' if app.workspace.logger else ''), f'''Workspace information:
CheeseAPI: <cyan><underline>{app.workspace.CheeseAPI}</underline></cyan>
Base: <cyan><underline>{app.workspace.base}</underline></cyan>''' + (f'''
Static: <cyan><underline>{app.workspace.static}</underline></cyan>''' if app.server.static else '') + (f'''
Log: <cyan><underline>{app.workspace.log}</underline></cyan>''' if app.workspace.logger else '') + (f'''
Logger: <cyan><underline>{app.workspace.logger}</underline></cyan>''' if app.workspace.logger else ''))

        logger.starting(f'''Server information:
Host: {app.server.host}
Port: {app.server.port}
Workers: {app.server.workers}''' + (f'''
Static: {app.server.static}''' if app.server.static else ''), f'''Server information:
Host: <cyan>{app.server.host}</cyan>
Port: <blue>{app.server.port}</blue>
Workers: <blue>{app.server.workers}</blue>''' + (f'''
Static: <cyan>{app.server.static}</cyan>''' if app.server.static else ''))

        progressBar = ProgressBar(20)

        moduleNum = len(app.modules)
        if moduleNum:
            logger.starting(f'''Modules:
''' + ' | '.join(app.modules), f'''Modules:
''' + ' | '.join(app.modules) + '''
''')
            timer = time.time()
            for i in range(moduleNum):
                message, styledMessage = progressBar(i * 1.0 / moduleNum)
                logger.loading(message, styledMessage)
                Module(app.modules[i])
            timer = time.time() - timer
            logger.loaded('The modules are loaded, which takes {:.6f} seconds'.format(timer), 'The modules are loaded, which takes <blue>{:.6f}</blue> seconds'.format(timer), refreshed = True)

        if app.localModules is True:
            localModule = []
            for foldername in os.listdir(app.workspace.base):
                if foldername[0] == '.' or foldername == '__pycache__':
                    continue
                folderPath = os.path.join(app.workspace.base, foldername)
                if os.path.isdir(folderPath):
                    if (not app.workspace.static or not os.path.exists(os.path.join(app.workspace.base, app.workspace.static)) or not os.path.samefile(folderPath, os.path.join(app.workspace.base, app.workspace.static))) and (not app.workspace.log or not os.path.exists(os.path.join(app.workspace.base, app.workspace.log)) or not os.path.samefile(folderPath, os.path.join(app.workspace.base, app.workspace.log))) and foldername not in app.exclude_localModules:
                        localModule.append(foldername)
            app.localModules = localModule
        else:
            app.preferred_localModules = []
        localModuleNum = len(app.localModules)
        if localModuleNum:
            logger.starting(f'''Local Modules:
''' + ' | '.join(app.localModules), f'''Local Modules:
''' + ' | '.join(app.localModules) + '''
''')
            timer = time.time()
            count = 0
            for module in app.preferred_localModules:
                message, styledMessage = progressBar(count * 1.0 / localModuleNum)
                logger.loading(message, styledMessage)
                LocalModule(app.workspace.base, module)
                count += 1
            for module in app.localModules:
                if module not in app.preferred_localModules:
                    message, styledMessage = progressBar(count * 1.0 / localModuleNum)
                    logger.loading(message, styledMessage)
                    LocalModule(app.workspace.base, module)
                    count += 1
            timer = time.time() - timer
            logger.loaded('The local modules are loaded, which takes {:.6f} seconds'.format(timer), 'The local modules are loaded, which takes <blue>{:.6f}</blue> seconds'.format(timer), refreshed = True)

    def worker_beforeStartingHandle(self, func: Callable):
        self.worker_beforeStartingHandles.append(func)

    def _worker_beforeStartingHandle(self):
        logger.debug(f'The subprocess {os.getpid()} started', f'The subprocess <blue>{os.getpid()}</blue> started')

    def worker_afterStartingHandle(self, func: Callable):
        self.worker_afterStartingHandles.append(func)

    def server_afterStartingHandle(self, func: Callable):
        self.server_afterStartingHandles.append(func)

    def _server_afterStartingHandle(self):
        from CheeseAPI.app import app

        logger.starting(f'The server started on http://{app.server.host}:{app.server.port}', f'The server started on <cyan><underline>http://{app.server.host}:{app.server.port}</underline></cyan>')

        timer = time.time() - app.g['timer']
        logger.starting('The server startup takes {:.6f} seconds'.format(timer), 'The server startup takes <blue>{:.6f}</blue> seconds'.format(timer))

    def context_beforeFirstRequestHandle(self, func: Callable):
        self.context_beforeFirstRequestHandles.append(func)

    def http_beforeRequestHandle(self, func: Callable):
        self.http_beforeRequestHandles.append(func)

    async def _http_staticHandle(self, protocol: 'Protocol', app: 'App'):
        try:
            return FileResponse(app.workspace.static[:-1] + protocol.request.path)
        except:
            ...

    async def _http_404Handle(self, protocol: 'Protocol', app: 'App'):
        return Response(status = http.HTTPStatus.NOT_FOUND)

    async def _http_optionsHandle(self, protocol: 'Protocol', app: 'App'):
        return Response(status = http.HTTPStatus.OK)

    async def _http_405Handle(self, protocol: 'Protocol', app: 'App'):
        return Response(status = http.HTTPStatus.METHOD_NOT_ALLOWED)

    async def _http_noResponseHandle(self, protocol: 'Protocol', app: 'App'):
        logger.danger(f'''An error occurred while accessing {protocol.request.method} {protocol.request.fullPath}:
A usable BaseResponse is not returned''', f'''An error occurred while accessing <cyan>{protocol.request.method} {protocol.request.fullPath}</cyan>:
A usable BaseResponse is not returned''')

        return Response(status = http.HTTPStatus.INTERNAL_SERVER_ERROR)

    async def _http_500Handle(self, protocol: 'Protocol', app: 'App', e: BaseException):
        message = logger.encode(traceback.format_exc()[:-1])
        logger.danger(f'''An error occurred while accessing {protocol.request.method} {protocol.request.fullPath}:
{message}''', f'''An error occurred while accessing <cyan>{protocol.request.method} {protocol.request.fullPath}</cyan>:
{message}''')

        return Response(status = http.HTTPStatus.INTERNAL_SERVER_ERROR)

    async def _http_responseHandle(self, protocol: 'Protocol', app: 'App', response: 'Response') -> bool:
        if isinstance(response, BaseResponse):
            if signal.receiver('http_afterResponseHandle'):
                await signal.async_send('http_afterResponseHandle', {
                    'response': response,
                    'request': protocol.request
                })
            for http_afterResponseHandle in self.http_afterResponseHandles:
                await http_afterResponseHandle(**{
                    'response': response,
                    'request': protocol.request
                })

            if app.cors.origin == '*':
                response.headers['Access-Control-Allow-Origin'] = app.cors.origin
            if len(app.cors.origin):
                response.headers['Access-Control-Allow-Origin'] = ', '.join(app.cors.origin)
            if len(app.cors.methods):
                response.headers['Access-Control-Allow-Methods'] = ', '.join(app.cors.methods)
            if app.cors.headers == '*':
                response.headers['Access-Control-Allow-Headers'] = app.cors.headers
            if len(app.cors.headers):
                response.headers['Access-Control-Allow-Headers'] = ', '.join(app.cors.headers)

            try:
                protocol.transport.write(await response())
                streamed = True
                while streamed:
                    content, streamed = await response()
                    protocol.transport.write(content)
            except:
                ...

            logger.http(f'The {protocol.request.headers.get("X-Forwarded-For").split(", ")[0]} accessed {protocol.request.method} {protocol.request.fullPath} and returned {response.status}', f'The <cyan>{protocol.request.headers.get("X-Forwarded-For").split(", ")[0]}</cyan> accessed <cyan>{protocol.request.method} ' + logger.encode(protocol.request.fullPath) + f'</cyan> and returned <blue>{response.status}</blue>')

            if protocol.transport.is_closing():
                return

            if protocol.timeoutTask:
                protocol.timeoutTask.cancel()
                protocol.timeoutTask = None
            protocol.timeoutTask = asyncio.get_event_loop().call_later(5.0, protocol.transport.close)
            protocol.task = None

            protocol.transport.resume_reading()

            if protocol.deque:
                _protocol = protocol.deque.popleft()
                _protocol.transport.resume_reading()
                protocol.task = asyncio.get_event_loop().create_task(app.handle._httpHandle(_protocol, app))
                protocol.task.add_done_callback(app.httpWorker.tasks.discard)
                app.httpWorker.tasks.add(protocol.task)

            return True
        return False

    def http_afterResponseHandle(self, func: Callable):
        self.http_afterResponseHandles.append(func)

    async def _websocket_requestHandle(self, protocol: 'WebsocketProtocol', app: 'App') -> Tuple[Callable, Dict[str, Any]] | HTTPResponse:
        funcs = paths.match(protocol.request.path)

        if not funcs:
            return await self._websocket_responseHandle(protocol, app, await self._websocket_404Handle(protocol, app))

        if 'WEBSOCKET' not in funcs:
            return await self._websocket_responseHandle(protocol, app, await self._websocket_405Handle(protocol, app))

        func = funcs['WEBSOCKET'][0]()
        kwargs = funcs['WEBSOCKET'][1]
        kwargs['request'] = protocol.request

        return func, kwargs

    async def _websocket_404Handle(self, protocol: 'WebsocketProtocol', app: 'App') -> Response:
        return Response(status = http.HTTPStatus.NOT_FOUND)

    async def _websocket_405Handle(self, protocol: 'WebsocketProtocol', app: 'App') -> Response:
        return Response(status = http.HTTPStatus.METHOD_NOT_ALLOWED)

    async def _websocket_responseHandle(self, protocol: 'WebsocketProtocol', app: 'App', response) -> HTTPResponse:
        for http_afterResponseHandle in self.http_afterResponseHandles:
            _response = await http_afterResponseHandle(**{
                'response': response,
                'request': protocol.request
            })
            if isinstance(_response, BaseResponse):
                response = _response

        logger.http(f'The {protocol.request.headers.get("X-Forwarded-For").split(", ")[0]} accessed WEBSOCKET {protocol.request.fullPath} and returned {response.status}', f'The <cyan>{protocol.request.headers.get("X-Forwarded-For").split(", ")[0]}</cyan> accessed <cyan>WEBSOCKET ' + logger.encode(protocol.request.fullPath) + f'</cyan> and returned <blue>{response.status}</blue>')

        return response.status, response.headers, response.body if isinstance(response.body, bytes) else str(response.body).encode()

    def _websocket_subprotocolHandle(self, protocol: 'WebsocketProtocol', app: 'App') -> str | None:
        kwargs = protocol.func[1]
        kwargs.update({
            'subprotocols': protocol.request.headers.get('Sec-Websocket-Protocol', '').split(', ')
        })
        return protocol.func[0].subprotocolHandle(**kwargs)

    def websocket_beforeConnectionHandle(self, func: Callable):
        self.websocket_beforeConnectionHandles.append(func)

    async def _websocket_connectionHandle(self, protocol: 'WebsocketProtocol', app: 'App'):
        try:
            logger.websocket(f'The {protocol.request.headers.get("X-Forwarded-For").split(", ")[0]} connected WEBSOCKET {protocol.request.fullPath}', f'The <cyan>{protocol.request.headers.get("X-Forwarded-For").split(", ")[0]}</cyan> connected <cyan>WEBSOCKET {protocol.request.fullPath}</cyan>')

            await protocol.func[0].connectionHandle(**protocol.func[1])
        except:
            message = logger.encode(traceback.format_exc()[:-1])
            logger.danger(f'''An error occurred while connecting WEBSOCKET {protocol.request.fullPath}:
{message}''', f'''An error occurred while connecting <cyan>WEBSOCKET {protocol.request.fullPath}</cyan>:
{message}''')

    async def _websocket_handler(self, protocol: 'WebsocketProtocol', app: 'App'):
        try:
            for websocket_beforeConnectionHandle in app.handle.websocket_beforeConnectionHandles:
                await websocket_beforeConnectionHandle(**protocol.func[1])
            if signal.receiver('websocket_beforeConnectionHandle'):
                await signal.async_send('websocket_beforeConnectionHandle', protocol.func[1])

            await app.handle._websocket_connectionHandle(protocol, app)

            while not protocol.closed:
                await app.handle._websocket_messageHandle(protocol, app)
        except:
            message = logger.encode(traceback.format_exc()[:-1])
            logger.danger(f'''An error occurred while receiving WEBSOCKET {protocol.request.fullPath} message:
{message}''', f'''An error occurred while receiving <cyan>WEBSOCKET {protocol.request.fullPath}</cyan> message:
{message}''')

    async def _websocket_messageHandle(self, protocol: 'WebsocketProtocol', app: 'App'):
        try:
            kwargs = protocol.func[1].copy()
            kwargs.update({
                'message': await protocol.recv()
            })
            await protocol.func[0].messageHandle(**kwargs)
        except websockets.exceptions.ConnectionClosedError:
            ...
        except websockets.exceptions.ConnectionClosedOK:
            ...
        except asyncio.exceptions.CancelledError:
            ...
        except:
            message = logger.encode(traceback.format_exc()[:-1])
            logger.danger(f'''An error occurred while receiving WEBSOCKET {protocol.request.fullPath} message:
{message}''', f'''An error occurred while receiving <cyan>WEBSOCKET {protocol.request.fullPath}</cyan> message:
{message}''')

    def websocket_afterDisconnectionHandle(self, func: Callable):
        self.websocket_afterDisconnectionHandles.append(func)

    def _websocket_disconnectionHandle(self, protocol: 'WebsocketProtocol', app: 'App'):
        if not protocol.func:
            return

        try:
            protocol.func[0].disconnectionHandle(**protocol.func[1])

            logger.websocket(f'The {protocol.request.headers.get("X-Forwarded-For").split(", ")[0]} disconnected WEBSOCKET {protocol.request.fullPath}', f'The <cyan>{protocol.request.headers.get("X-Forwarded-For").split(", ")[0]}</cyan> disconnected <cyan>WEBSOCKET {protocol.request.fullPath}</cyan>')

            if signal.receiver('websocket_afterDisconnectionHandle'):
                signal.send('websocket_afterDisconnectionHandle', protocol.func[1])
            for websocket_afterDisconnectionHandle in app.handle.websocket_afterDisconnectionHandles:
                websocket_afterDisconnectionHandle(**protocol.func[1])
        except:
            message = logger.encode(traceback.format_exc()[:-1])
            logger.danger(f'''An error occurred while disconnecting WEBSOCKET {protocol.request.fullPath}:
{message}''', f'''An error occurred while disconnecting <cyan>WEBSOCKET {protocol.request.fullPath}</cyan>:
{message}''')

    def worker_beforeStoppingHandle(self, func: Callable):
        self.worker_beforeStoppingHandles.append(func)

    def _worker_beforeStoppingHandle(self):
        logger.debug(f'The {os.getpid()} subprocess stopped', f'The <blue>{os.getpid()}</blue> subprocess stopped')

    def server_beforeStoppingHandle(self, func: Callable):
        self.server_beforeStoppingHandles.append(func)

    def _server_beforeStoppingHandle(self):
        from CheeseAPI.app import app

        timer = time.time() - app.g['timer']
        message = 'The server runs for a total of '
        styledMessage = 'The server runs for a total of '
        days = int(timer // 86400)
        if days:
            message += f'{days} days'
            styledMessage += f'<blue>{days}</blue> days '
        hours = int(timer % 24 // 3600)
        if days or hours:
            message += f'{hours} hours'
            styledMessage += f'<blue>{hours}</blue> hours '
        minutes = int(timer % 3600 // 60)
        if days or hours or minutes:
            message += f'{minutes} minutes '
            styledMessage += f'<blue>{minutes}</blue> minutes '
        message += '{:.6f} seconds'.format(timer % 60)
        styledMessage += '<blue>{:.6f}</blue> seconds'.format(timer % 60)
        logger.ending(message, styledMessage)
        logger.ending(f'The master process {os.getpid()} stopped', f'The master process <blue>{os.getpid()}</blue> stopped')
