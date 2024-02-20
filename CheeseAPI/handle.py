import os, time, http, traceback, asyncio
from typing import TYPE_CHECKING, Callable, Tuple, Dict, Any

import websockets
from CheeseLog import logger, ProgressBar
from websockets.legacy.server import HTTPResponse

from CheeseAPI.response import FileResponse, BaseResponse, Response
from CheeseAPI.signal import signal
from CheeseAPI.module import Module, LocalModule

if TYPE_CHECKING:
    from CheeseAPI.app import App
    from CheeseAPI.protocol import WebsocketProtocol, Protocol

class Handle:
    async def _httpHandle(self, protocol: 'Protocol', app: 'App'):
        try:
            if app.server.static and protocol.request.path.startswith(app.server.static) and protocol.request.method == http.HTTPMethod.GET:
                try:
                    await self._http_responseHandle(protocol, app, await self._http_staticHandle(protocol, app))
                    return
                except:
                    ...

            try:
                func, kwargs = app.routeBus._match(protocol.request.path, protocol.request.method)

                if signal.receiver('http_beforeRequestHandle'):
                    await signal.async_send('http_beforeRequestHandle', { 'request': protocol.request })

                kwargs['request'] = protocol.request
                response = await func(**kwargs)
                if await self._http_responseHandle(protocol, app, response):
                    return

                await self._http_responseHandle(protocol, app, await self._http_noResponseHandle(protocol, app))
            except KeyError as e:
                if protocol.request.method == http.HTTPMethod.OPTIONS and (app.cors.origin == '*' or protocol.request.method in app.cors.origin):
                    await self._http_responseHandle(protocol, app, await self._http_optionsHandle(protocol, app))
                    return

                if e.args[0] == 0:
                    await self._http_responseHandle(protocol, app, await self._http_404Handle(protocol, app))
                    return

                if e.args[0] == 1:
                    await self._http_responseHandle(protocol, app, await self._http_405Handle(protocol, app))
                    return
        except BaseException as e:
            await self._http_responseHandle(protocol, app, await self._http_500Handle(protocol, app, e))

    def _exitSignalHandle(self, server):
        server.close()

    def _server_beforeStartingHandle(self, app: 'App'):
        app.g['startTimer'] = time.time()

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

        moduleNum = len(app.modules)
        if moduleNum:
            progressBar = ProgressBar()
            message, styledMessage = progressBar(0)
            logger.loading(message, styledMessage, refreshed = False)
            for i in range(moduleNum):
                Module(app.modules[i])
                message, styledMessage = progressBar((i + 1) / moduleNum)
                logger.loading('Modules: ' + message + ' ' + app.modules[i], 'Modules: ' + styledMessage + ' ' + app.modules[i])

            logger.loaded(f'''Modules:
''' + ' | '.join(app.modules), refreshed = True)

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
            progressBar = ProgressBar()
            i = 0
            message, styledMessage = progressBar(i / localModuleNum)
            logger.loading(message, styledMessage, refreshed = False)
            for module in app.preferred_localModules:
                LocalModule(app.workspace.base, module)
                i += 1
                message, styledMessage = progressBar(i / localModuleNum)
                logger.loading('Local Modules: ' + message + ' ' + module, 'Local Modules: ' + styledMessage + ' ' + module)
            for module in app.localModules:
                if module not in app.preferred_localModules:
                    LocalModule(app.workspace.base, module)
                    i += 1
                    message, styledMessage = progressBar(i / localModuleNum)
                    logger.loading('Local Modules: ' + message + ' ' + module, 'Local Modules: ' + styledMessage + ' ' + module)

            logger.loaded(f'''Local Modules:
''' + ' | '.join(app.localModules), refreshed = True)

    def _worker_beforeStartingHandle(self):
        logger.debug(f'The subprocess {os.getpid()} started', f'The subprocess <blue>{os.getpid()}</blue> started')

    def _server_afterStartingHandle(self, app: 'App'):
        logger.starting(f'The server started on http://{app.server.host}:{app.server.port}', f'The server started on <cyan><underline>http://{app.server.host}:{app.server.port}</underline></cyan>')

    async def _http_staticHandle(self, protocol: 'Protocol', app: 'App'):
        return FileResponse(app.workspace.static[:-1] + protocol.request.path)

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
                return True

            protocol.task = None

            protocol.transport.resume_reading()

            if protocol.deque:
                _protocol = protocol.deque.popleft()
                _protocol.transport.resume_reading()
                protocol.task = asyncio.get_event_loop().create_task(app._handle._httpHandle(_protocol, app))
                protocol.task.add_done_callback(app.httpWorker.tasks.discard)
                app.httpWorker.tasks.add(protocol.task)

            return True
        return False

    async def _websocket_requestHandle(self, protocol: 'WebsocketProtocol', app: 'App') -> Tuple[Callable, Dict[str, Any]] | HTTPResponse:
        try:
            func, kwargs = app.routeBus._match(protocol.request.path, 'WEBSOCKET')
            kwargs['request'] = protocol.request
            return func(), kwargs
        except KeyError as e:
            if e.args[0] == 0:
                return await self._websocket_responseHandle(protocol, app, await self._websocket_404Handle(protocol, app))

            if e.args[0] == 1:
                return await self._websocket_responseHandle(protocol, app, await self._websocket_405Handle(protocol, app))

    async def _websocket_404Handle(self, protocol: 'WebsocketProtocol', app: 'App') -> Response:
        return Response(status = http.HTTPStatus.NOT_FOUND)

    async def _websocket_405Handle(self, protocol: 'WebsocketProtocol', app: 'App') -> Response:
        return Response(status = http.HTTPStatus.METHOD_NOT_ALLOWED)

    async def _websocket_responseHandle(self, protocol: 'WebsocketProtocol', app: 'App', response: BaseResponse) -> HTTPResponse:
        if signal.receiver('http_afterResponseHandle'):
            await signal.async_send('http_afterResponseHandle', {
                'response': response,
                'request': protocol.request
            })

        logger.http(f'The {protocol.request.headers.get("X-Forwarded-For").split(", ")[0]} accessed WEBSOCKET {protocol.request.fullPath} and returned {response.status}', f'The <cyan>{protocol.request.headers.get("X-Forwarded-For").split(", ")[0]}</cyan> accessed <cyan>WEBSOCKET ' + logger.encode(protocol.request.fullPath) + f'</cyan> and returned <blue>{response.status}</blue>')

        return response.status, response.headers, response.body if isinstance(response.body, bytes) else str(response.body).encode()

    def _websocket_subprotocolHandle(self, protocol: 'WebsocketProtocol', app: 'App') -> str | None:
        kwargs = protocol.func[1]
        kwargs.update({
            'subprotocols': protocol.request.headers.get('Sec-Websocket-Protocol', '').split(', ')
        })
        return protocol.func[0].subprotocolHandle(**kwargs)

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
            protocol.is_alive = True

            if signal.receiver('websocket_beforeConnectionHandle'):
                await signal.async_send('websocket_beforeConnectionHandle', protocol.func[1])

            await app._handle._websocket_connectionHandle(protocol, app)

            while not protocol.closed:
                await app._handle._websocket_messageHandle(protocol, app)
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

    def _websocket_disconnectionHandle(self, protocol: 'WebsocketProtocol', app: 'App'):
        if not protocol.func:
            return

        try:
            protocol.func[0].disconnectionHandle(**protocol.func[1])

            logger.websocket(f'The {protocol.request.headers.get("X-Forwarded-For").split(", ")[0]} disconnected WEBSOCKET {protocol.request.fullPath}', f'The <cyan>{protocol.request.headers.get("X-Forwarded-For").split(", ")[0]}</cyan> disconnected <cyan>WEBSOCKET {protocol.request.fullPath}</cyan>')

            if signal.receiver('websocket_afterDisconnectionHandle'):
                signal.send('websocket_afterDisconnectionHandle', protocol.func[1])
        except:
            message = logger.encode(traceback.format_exc()[:-1])
            logger.danger(f'''An error occurred while disconnecting WEBSOCKET {protocol.request.fullPath}:
{message}''', f'''An error occurred while disconnecting <cyan>WEBSOCKET {protocol.request.fullPath}</cyan>:
{message}''')

    def _worker_beforeStoppingHandle(self, app: 'App'):
        logger.debug(f'The {os.getpid()} subprocess stopped', f'The <blue>{os.getpid()}</blue> subprocess stopped')

    def _server_beforeStoppingHandle(self, app: 'App'):
        timer = time.time() - app.g['startTimer']
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
