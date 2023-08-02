import os, time, inspect, traceback, multiprocessing, json, shutil
from typing import Callable, AsyncIterator, Dict, List, Any, Set
from multiprocessing.process import BaseProcess

import CheeseLog, asyncio
from CheeseLog import logger, Logger

from . import exception
from .route import Route, matchPath
from .request import Request
from .response import Response, BaseResponse, FileResponse
from .file import File
from .websocket import websocket
from .module import LocalModule, Module
from .cSignal import signal

class App:
    def __init__(self):
        self.startTimer: float = time.time()

        from .system import System
        from .workspace import Workspace
        from .server import Server

        self.process: BaseProcess = multiprocessing.current_process()
        self.logger: Logger = logger

        self.system: System = System()
        self.workspace: Workspace = Workspace()
        self.server: Server = Server(self)
        self.modules: Set[Module] | Set[str] = set()
        self.localModules: Set[LocalModule] | Set[str] | bool = True
        self.exclude_localModules: Set[LocalModule] = set()

        self.route: Route = Route('')

        self.server_startingHandles: List[Callable] = []
        self.server_endingHandles: List[Callable] = []
        # http
        self.http_response404Handles: List[Callable] = []
        self.http_response405Handles: List[Callable] = []
        self.http_response500Handles: List[Callable] = []
        self.http_beforeRequestHandles: List[Callable] = []
        self.http_afterResponseHandles: List[Callable] = []
        # websocket
        self.websocket_beforeConnectionHandles: List[Callable] = []
        self.websocket_afterDisconnectHandles: List[Callable] = []
        self.websocket_errorHandles: List[Callable] = []
        self.websocket_notFoundHandles: List[Callable] = []

        if os.path.exists(self.workspace.BASE_PATH + '/.cache/config.json'):
            with open(self.workspace.BASE_PATH + '/.cache/config.json', 'r') as f:
                data = json.load(f)
            self.workspace.LOG_PATH = data['workspace']['LOG_PATH']
            self.server.HOST = data['server']['HOST']
            self.server.PORT = data['server']['PORT']
            self.server.IS_RELOAD = data['server']['IS_RELOAD']
            self.server.WORKERS = data['server']['WORKERS']
            self.server.LOG_FILENAME = data['server']['LOG_FILENAME']
            with open(self.workspace.BASE_PATH + '/.cache/workers', 'a+') as f:
                f.write('1')
                f.seek(0)
                workers = len(f.readline())
            if workers == self.server.WORKERS and os.path.exists(self.workspace.BASE_PATH + '/.cache'):
                shutil.rmtree(self.workspace.BASE_PATH + '/.cache')

    async def __call__(self, scope, receive, send):
        ''' Server started '''
        if scope['type'] == 'lifespan':
            message = await receive()
            if message['type'] == 'lifespan.startup':
                _modules = set()
                if self.process.name == 'MainProcess' and len(self.modules):
                    CheeseLog.starting(f'Modules:\n{" | ".join(self.modules)}')
                for module in self.modules:
                    _modules.add(Module(_modules, module))
                self.modules = _modules

                if self.localModules is True:
                    self.localModules = set()
                    for folderName in os.listdir(self.workspace.BASE_PATH):
                        if folderName[0] == '.':
                            continue
                        if folderName in self.exclude_localModules:
                            continue
                        folderPath = os.path.join(self.workspace.BASE_PATH, folderName)
                        if os.path.isdir(folderPath) and folderPath not in [ self.workspace.BASE_PATH + self.workspace.STATIC_PATH[:-1], self.workspace.BASE_PATH + self.workspace.MEDIA_PATH[:-1], self.workspace.BASE_PATH + self.workspace.LOG_PATH[:-1], self.workspace.BASE_PATH + '/__pycache__' ]:
                            self.localModules.add(folderName)
                if self.process.name == 'MainProcess' and len(self.localModules):
                    CheeseLog.starting(f'Local modules:\n{" | ".join(self.localModules)}')
                _localModules = set()
                for module in self.localModules:
                    _localModules.add(LocalModule(self.workspace.BASE_PATH, module))
                self.localModules = _localModules

                startTime = time.time() - self.startTimer
                if self.process.name == 'MainProcess':
                    CheeseLog.starting('The server started, took {:.6f} seconds'.format(startTime), 'The server started, took \033[34m{:.6f}\033[0m seconds'.format(startTime))
                else:
                    CheeseLog.starting(f'The worker {os.getpid()} started, took ' + '{:.6f} seconds'.format(startTime), f'The worker \033[34m{os.getpid()}\033[0m started, took ' + '\033[34m{:.6f}\033[0m seconds'.format(startTime))

        ''' Http request '''
        if scope['type'] in [ 'http', 'https' ]:
            try:
                timer = time.time()
                body = b''
                bodyFlag = True
                while bodyFlag:
                    message = await receive()
                    body += message.get('body', b'')
                    bodyFlag = message.get('more_body', False)
                request = Request(scope, body)
                response = None
                requestFunc = None

                # Static
                if self.server.STATIC_PATH and request.path.startswith(self.server.STATIC_PATH):
                    try:
                        response = FileResponse(File(path = self.workspace.STATIC_PATH + request.path[len(self.server.STATIC_PATH):]))
                    except:
                        ...

                if not isinstance(response, FileResponse):
                    # 404
                    requestFunc, kwargs = matchPath(request.path)
                    kwargs['request'] = request
                    if not isinstance(requestFunc, dict):
                        if signal.receiver('http_response404Handle'):
                            await signal.send_async('http_response404Handle', kwargs)
                        for http_response404Handle in self.http_response404Handles:
                            _response = await self.doFunc(http_response404Handle, kwargs)
                            if isinstance(_response, BaseResponse):
                                response = _response
                        if not isinstance(response, BaseResponse):
                            response = Response(status = 404)

                    # 405
                    elif request.method not in requestFunc:
                        if signal.receiver('http_response405Handle'):
                            await signal.send_async('http_response405Handle', kwargs)
                        for http_response405Handle in self.http_response405Handles:
                            _response = await self.doFunc(http_response405Handle, kwargs)
                            if isinstance(_response, BaseResponse):
                                response = _response
                        if not isinstance(response, BaseResponse):
                            response = Response(status = 405)

                    # Other...
                    else:
                        if signal.receiver('http_beforeRequestHandle'):
                            await signal.send_async('http_beforeRequestHandle', kwargs)
                        for http_beforeRequestHandle in self.http_beforeRequestHandles:
                            _response = await self.doFunc(http_beforeRequestHandle, kwargs)
                            if isinstance(_response, BaseResponse):
                                response = _response

                        if not isinstance(response, BaseResponse):
                            requestFunc = requestFunc[request.method]
                            response = await self.doFunc(requestFunc, kwargs)

                        if isinstance(response, BaseResponse):
                            if signal.receiver('http_afterResponseHandle'):
                                await signal.send_async('http_afterResponseHandle', kwargs)
                            for http_afterResponseHandle in self.http_afterResponseHandles:
                                kwargs['response'] = response
                                _response = await self.doFunc(http_afterResponseHandle, kwargs)
                                if isinstance(_response, BaseResponse):
                                    response = _response
                        else:
                            CheeseLog.danger(f'The error occured while accessing the {request.method} {request.fullPath}\nTraceback (most recent call last):\n  File "{inspect.getsourcefile(requestFunc)}", line {inspect.getsourcelines(requestFunc)[1]}, in <module>\n    Function {requestFunc.__name__} needs to return Response, not {response.__class__.__name__}')
                            response = Response(status = 500)
            except Exception as e:
                CheeseLog.danger(f'The error occured while accessing the {request.method} {request.fullPath}\n{traceback.format_exc()}'[:-1], f'The error occured while accessing the \033[36m{request.method} {request.fullPath}\033[0m\n{traceback.format_exc()}'[:-1])
                if signal.receiver('http_response500Handle'):
                    await signal.send_async('http_response500Handle', kwargs)
                for http_response500Handle in self.http_response500Handles:
                    kwargs['exception'] = e
                    _response = await self.doFunc(http_response500Handle, kwargs)
                    if isinstance(_response, BaseResponse):
                        response = _response
                if not isinstance(response, BaseResponse):
                    response = Response(status = 500)

            headers = []
            for key, value in response.headers.items():
                headers.append([key.encode(), value.encode()])
            await send({
                'type': 'http.response.start',
                'status': response.status,
                'headers': headers
            })

            body = response.body
            if isinstance(response.body, Callable):
                body = response.body()
            if isinstance(body, AsyncIterator):
                try:
                    async for value in body:
                        if isinstance(body, bytes):
                            await send({
                                'type': 'http.response.body',
                                'body': value,
                                'more_body': True
                            })
                        else:
                            await send({
                                'type': 'http.response.body',
                                'body': str(value).encode(),
                                'more_body': True
                            })
                except Exception as e:
                    await send({
                        'type': 'http.response.body',
                        'body': b''
                    })
            else:
                if isinstance(body, bytes):
                    await send({
                        'type': 'http.response.body',
                        'body': body
                    })
                else:
                    await send({
                        'type': 'http.response.body',
                        'body': str(body).encode()
                    })

            diffTime = time.time() - timer
            CheeseLog.http(f'{request.ip} accessed {request.method} {request.fullPath}, returned {response.status}, took ' + '{:.6f}'.format(diffTime) + ' seconds', f'{request.ip} accessed \033[36m{request.method} {request.fullPath}\033[0m, returned \033[34m{response.status}\033[0m, took ' + '\033[34m{:.6f}\033[0m'.format(diffTime) + ' seconds')

        ''' Websocket '''
        if scope['type'] in [ 'websocket', 'websockets' ]:
            try:
                request = Request(scope)
                requestFunc, kwargs = matchPath(request.path)
                kwargs['request'] = request
                if requestFunc is None or 'WEBSOCKET' not in requestFunc:
                    for websocket_notFoundHandle in self.websocket_notFoundHandles:
                        await self.doFunc(websocket_notFoundHandle, kwargs)
                    return
                requestFunc = requestFunc['WEBSOCKET']

                if signal.receiver('websocket_beforeConnectionHandle'):
                    await signal.send_async('websocket_beforeConnectionHandle', kwargs)
                for websocket_beforeConnectionHandle in self.websocket_beforeConnectionHandles:
                    await self.doFunc(websocket_beforeConnectionHandle, kwargs)

                await send({
                    'type': 'websocket.accept'
                })

                if (await receive())['type'] == 'websocket.connect':
                    CheeseLog.websocket(f'{request.ip} connected {request.path}', f'{request.ip} connected \033[36m{request.path}\033[0m')

                    websocket._CLIENTS[request.sid] = asyncio.Queue()
                    async def sendHandle():
                        try:
                            while True:
                                await (await websocket._CLIENTS[request.sid].get())(send)
                        except asyncio.CancelledError:
                            ...
                    task = asyncio.create_task(sendHandle())

                    while True:
                        message = await receive()
                        if message['type'] == 'websocket.receive':
                            if 'text' in message:
                                kwargs['value'] = message['text']
                            elif 'bytes' in message:
                                kwargs['value'] = message['bytes']
                            await self.doFunc(requestFunc, kwargs)
                        elif message['type'] == 'websocket.disconnect':
                            del websocket._CLIENTS[request.sid]
                            task.cancel()
                            await task
                            CheeseLog.websocket(f'{request.ip} disconnected {request.path}', f'{request.ip} disconnected \033[36m{request.path}\033[0m')
                            break

                if signal.receiver('websocket_afterDisconnectHandle'):
                    await signal.send_async('websocket_afterDisconnectHandle', kwargs)
                for websocket_afterDisconnectHandle in self.websocket_afterDisconnectHandles:
                    await self.doFunc(websocket_afterDisconnectHandle, kwargs)
            except Exception as e:
                CheeseLog.danger(f'The error occured while accessing the WEBSOCKET {request.fullPath}\n{traceback.format_exc()}'[:-1], f'The error occured while accessing the \033[36mWEBSOCKET {request.fullPath}\033[0m\n{traceback.format_exc()}'[:-1])
                for websocket_errorHandle in self.websocket_errorHandles:
                    kwargs['exception'] = e
                    await self.doFunc(websocket_errorHandle, kwargs)

    async def doFunc(self, func: Callable, kwargs: Dict[str, Any] = {}):
        _kwargs = {}
        sig = inspect.signature(func)
        for key, value in kwargs.items():
            if key in sig.parameters or 'kwargs' in sig.parameters:
                _kwargs[key] = value
        if inspect.iscoroutinefunction(func):
            return await func(**_kwargs)
        else:
            return func(**_kwargs)

    def server_startingHandle(self, func: Callable):
        self.server_startingHandles.append(func)

    def server_endingHandle(self, func: Callable):
        self.server_endingHandles.append(func)

    def http_response404Handle(self, func: Callable):
        self.http_response404Handles.append(func)

    def http_response405Handle(self, func: Callable):
        self.http_response405Handles.append(func)

    def http_response500Handle(self, func: Callable):
        self.http_response500Handles.append(func)

    def http_beforeRequestHandle(self, func: Callable):
        self.http_beforeRequestHandles.append(func)

    def http_afterResponseHandle(self, func: Callable):
        self.http_afterResponseHandles.append(func)

    def websocket_beforeConnectionHandle(self, func: Callable):
        self.websocket_beforeConnectionHandles.append(func)

    def websocket_afterDisconnectHandle(self, func: Callable):
        self.websocket_afterDisconnectHandles.append(func)

    def websocket_errorHandle(self, func: Callable):
        self.websocket_errorHandles.append(func)

app: App = App()
