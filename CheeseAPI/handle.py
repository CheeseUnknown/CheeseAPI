import time, os, inspect, socket, multiprocessing, signal, http, ipaddress
from typing import TYPE_CHECKING, Dict, Tuple, List

import asyncio, uvloop, setproctitle, websockets
from CheeseLog import logger

from CheeseAPI.response import BaseResponse, FileResponse, Response

if TYPE_CHECKING:
    from CheeseAPI.app import App
    from CheeseAPI.protocol import HttpProtocol, WebsocketProtocol

class Handle:
    def __init__(self, app: 'App'):
        self._app: 'App' = app

    def server_beforeStarting(self):
        self._app.g['startTime'] = time.time()

        for text in self._app._text.server_information():
            logger.starting(text[0], text[1])

        self.loadModules()
        self.loadLocalModules()

    def loadModule(self, name: str):
        module = __import__(name)
        type = getattr(module, 'CheeseAPI_module_type', 'single')
        dependencies = getattr(module, 'CheeseAPI_module_dependencies', [])
        preferredSubModules = getattr(module, 'CheeseAPI_module_preferredSubModules', [])

        # 依赖
        if dependencies:
            for dependency in dependencies:
                self.loadModule(dependency)

        modulePath = os.path.dirname(inspect.getfile(module))
        # 单模块
        if type == 'single':
            for filename in os.listdir(modulePath):
                filePath = os.path.join(modulePath, filename)
                if os.path.isfile(filePath) and filename.endswith('.py'):
                    __import__(f'{name}.{filename[:-3]}', fromlist = [''])
        # 多模块
        elif type == 'multiple':
            foldernames = os.listdir(modulePath)
            for foldername in preferredSubModules:
                foldername = f'{name}.{foldername}'
                if foldername in foldernames:
                    foldernames.remove(foldername)
                foldernames.insert(0, foldername)

            for foldername in foldernames:
                if foldername == '__pycache__':
                    continue

                folderPath = os.path.join(modulePath, foldername)
                if os.path.isdir(folderPath):
                    for filename in os.listdir(folderPath):
                        filePath = os.path.join(folderPath, filename)
                        if os.path.isfile(filePath) and filename.endswith('.py'):
                            __import__(f'{name}.{foldername}.{filename[:-3]}', fromlist = [''])

    def loadModules(self):
        moduleNum = len(self._app.modules)
        if moduleNum:
            print()

            for i in range(moduleNum):
                message, styledMessage = self._app._text.loadingModule(i / moduleNum, self._app.modules[i])
                logger.loading(message, styledMessage)

                self.loadModule(self._app.modules[i])

            for text in self._app._text.loadedModules():
                logger.loaded(text[0], text[1], refreshed = True)

    def loadLocalModule(self, name: str):
        modulePath = os.path.join(self._app.workspace.base, name)
        for filename in os.listdir(modulePath):
            filePath = os.path.join(modulePath, filename)
            if os.path.isfile(filePath) and filename.endswith('.py'):
                __import__(f'{name}.{filename[:-3]}', fromlist = [''])

    def loadLocalModules(self):
        foldernames = self._app.localModules.copy()
        for foldername in self._app.preferred_localModules:
            if foldername in foldernames:
                foldernames.remove(foldername)
                foldernames.insert(0, foldername)
        for foldername in self._app.exclude_localModules:
            if foldername in foldernames:
                foldernames.remove(foldername)

        moduleNum = len(foldernames)
        if moduleNum:
            print()

            for i in range(moduleNum):
                message, styledMessage = self._app._text.loadingLocalModule(i / moduleNum, foldernames[i])
                logger.loading(message, styledMessage)

                self.loadLocalModule(foldernames[i])

            for text in self._app._text.loadedLocalModules():
                logger.loaded(text[0], text[1], refreshed = True)

    def server_start(self):
        self._app._handle.server_beforeStarting()
        if self._app.signal.server_beforeStarting.receivers:
            self._app.signal.server_beforeStarting.send()

        try:
            ipaddress.IPv4Address(self._app.server.host)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except ipaddress.AddressValueError:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self._app.server.host, self._app.server.port))
        sock.listen(self._app.server.backlog)
        sock.set_inheritable(True)

        processes: List[multiprocessing.Process] = []
        multiprocessing.allow_connection_pickling()
        for i in range(self._app.server.workers - 1):
            process = multiprocessing.Process(target = self.worker_start, args = (sock,), name = self._app._text.workerProcess_title)
            process.start()
            processes.append(process)

        self.worker_start(sock, True)

        for process in processes:
            process.terminate()
            process.join()

        for text in self._app._text.server_stopping():
            logger.ending(text[0], text[1])

        self.server_afterStopping()
        if self._app.signal.server_afterStopping.receivers:
            self._app.signal.server_afterStopping.send()

        logger.destroy()

        os.killpg(os.getpid(), signal.SIGKILL)

    def worker_beforeStarting(self):
        for text in self._app._text.worker_starting():
            logger.debug(text[0], text[1])

    def worker_start(self, sock, master: bool = False):
        if not master:
            setproctitle.setproctitle(self._app._text.workerProcess_title)

        self.worker_beforeStarting()
        if self._app.signal.worker_beforeStarting.receivers:
            self._app.signal.worker_beforeStarting.send()

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        asyncio.run(self.worker_run(sock, master))

        with self._app._managers['lock']:
            self._app._managers['server.workers'].value -= 1

            for text in self._app._text.worker_stopping():
                logger.debug(text[0], text[1])

            self.worker_afterStopping()
            if self._app.signal.worker_afterStopping.receivers:
                self._app.signal.worker_afterStopping.send()

    async def worker_run(self, sock, master: bool):
        from CheeseAPI.app import app
        from CheeseAPI.protocol import HttpProtocol

        app.g = self._app.g
        app.managers = self._app.managers
        app._managers = self._app._managers

        loop = asyncio.get_running_loop()
        server = await loop.create_server(HttpProtocol, sock = sock)
        loop.add_signal_handler(signal.SIGINT, lambda server: server.close(), server)
        loop.add_signal_handler(signal.SIGTERM, lambda server: server.close(), server)

        await self.worker_afterStarting()
        if self._app.signal.worker_afterStarting.receivers:
            await self._app.signal.worker_afterStarting.send_async()

        with self._app._managers['lock']:
            self._app._managers['server.workers'].value += 1
            if self._app._managers['server.workers'].value == self._app.server.workers:
                for text in self._app._text.server_starting():
                    logger.starting(text[0], text[1])

                await self.server_afterStarting()
                if self._app.signal.server_afterStarting.receivers:
                    await self._app.signal.server_afterStarting.send_async()

        while server.is_serving():
            if master:
                await self.server_running()
                if self._app.signal.server_running.receivers:
                    await self._app.signal.server_running.send_async()

            await self.worker_running()
            if self._app.signal.worker_running.receivers:
                await self._app.signal.worker_running.send_async()

            await asyncio.sleep(self._app.server.intervalTime)

        with self._app._managers['lock']:
            if self._app._managers['server.workers'].value == self._app.server.workers:
                await self.server_beforeStopping()
                if self._app.signal.server_beforeStopping.receivers:
                    await self._app.signal.server_beforeStopping.send_async()

            await self.worker_beforeStopping()
            if self._app.signal.worker_beforeStopping.receivers:
                await self._app.signal.worker_beforeStopping.send_async()

    async def worker_afterStarting(self):
        ...

    async def server_afterStarting(self):
        ...

    async def server_running(self):
        ...

    async def worker_running(self):
        ...

    async def http_beforeRequest(self, protocol: 'HttpProtocol'):
        ...

    async def http_afterRequest(self, protocol: 'HttpProtocol'):
        ...

    async def http(self, protocol: 'HttpProtocol'):
        try:
            await self._app._handle.http_beforeRequest(self)
            if self._app.signal.http_beforeRequest.receivers:
                await self._app.signal.http_beforeRequest.send_async()

            await self.http_static(protocol)
            if isinstance(protocol.response, BaseResponse):
                if self._app.signal.http_static.receivers:
                    await self._app.signal.http_static.send_async(**{
                        'request': protocol.request,
                        'response': protocol.response,
                        **protocol.kwargs
                    })
                await self.http_response(protocol)
                return

            try:
                func, protocol.kwargs = self._app.routeBus._match(protocol.request.path, protocol.request.method)
            except KeyError as e:
                await self.http_afterRequest(protocol)
                if self._app.signal.http_afterRequest.receivers:
                    await self._app.signal.http_afterRequest.send_async(**{
                        'request': protocol.request,
                        **protocol.kwargs
                    })

                if e.args[0] == 0:
                    await self.http_404(protocol)
                    if self._app.signal.http_404.receivers:
                        await self._app.signal.http_404.send_async(**{
                            'request': protocol.request,
                            'response': protocol.response,
                            **protocol.kwargs
                        })
                    await self.http_response(protocol)
                    return

                if e.args[0] == 1:
                    if protocol.request.method == http.HTTPMethod.OPTIONS:
                        protocol.response = Response(status = 200)

                        if self._app.signal.http_options.receivers:
                            await self._app.signal.http_options.send_async(**{
                                'request': protocol.request,
                                'response': protocol.response,
                                **protocol.kwargs
                            })
                        await self.http_response(protocol)
                        return

                    await self.http_405(protocol)
                    if self._app.signal.http_405.receivers:
                        await self._app.signal.http_405.send_async(**{
                            'request': protocol.request,
                            'response': protocol.response,
                            'e': e,
                            **protocol.kwargs
                        })
                    await self.http_response(protocol)
                    return

                raise e

            await self.http_afterRequest(protocol)
            if self._app.signal.http_afterRequest.receivers:
                await self._app.signal.http_afterRequest.send_async(**{
                    'request': protocol.request,
                    **protocol.kwargs
            })

            protocol.response = await func(**{
                'request': protocol.request,
                **protocol.kwargs
            })

            await self.http_response(protocol)
        except BaseException as e:
            try:
                await self.http_500(protocol, e)
                if self._app.signal.http_500.receivers:
                    await self._app.signal.http_500.send_async(**{
                        'request': protocol.request,
                        'response': protocol.response,
                        'e': e,
                        **protocol.kwargs
                    })
                await self.http_response(protocol)
            except BaseException as e:
                await self.http_500(protocol, e, True)
                await self.http_response(protocol, True)

    async def http_static(self, protocol: 'HttpProtocol'):
        if self._app.server.static and self._app.workspace.static and protocol.request.path.startswith(self._app.server.static) and protocol.request.method == http.HTTPMethod.GET:
            try:
                protocol.response = FileResponse(os.path.join(self._app.workspace.static, protocol.request.path[1:]))

                await self.http_afterRequest(protocol)
                if self._app.signal.http_afterRequest.receivers:
                    await self._app.signal.http_afterRequest.send_async(**{
                        'request': protocol.request,
                        **protocol.kwargs
                    })

                if self._app.signal.http_static.receivers:
                    await self._app.signal.http_static.send_async(**{
                        'request': protocol.request,
                        **protocol.kwargs
                    })
            except (FileNotFoundError, IsADirectoryError):
                ...

    async def http_options(self, protocol: 'HttpProtocol'):
        protocol.response = Response(status = http.HTTPStatus.OK)

    async def http_404(self, protocol: 'HttpProtocol'):
        protocol.response = Response(status = http.HTTPStatus.NOT_FOUND)

    async def http_405(self, protocol: 'HttpProtocol'):
        protocol.response = Response(status = http.HTTPStatus.METHOD_NOT_ALLOWED)

    async def http_500(self, protocol: 'HttpProtocol', e: BaseException, recycled: bool = False):
        protocol.response = Response(status = http.HTTPStatus.INTERNAL_SERVER_ERROR)

        if not recycled:
            for text in self._app._text.http_500(protocol, e):
                logger.danger(text[0], text[1])

    async def http_response(self, protocol: 'HttpProtocol', recycled: bool = False):
        if not isinstance(protocol.response, BaseResponse):
            await self.noResponse(protocol)

        if not recycled:
            await self.http_beforeResponse(protocol)
            if self._app.signal.http_beforeResponse.receivers:
                await self._app.signal.http_beforeResponse.send_async(**{
                    'request': protocol.request,
                    'response': protocol.response,
                    **protocol.kwargs
                })

        if (
            (
                protocol.request.origin not in self._app.cors.exclude_origin
                and
                (
                    self._app.cors.origin == '*'
                    or
                    protocol.request.origin in self._app.cors.origin
                )
            )
            and (
                self._app.cors.methods == '*'
                or
                protocol.request.method in self._app.cors.methods
            )
        ):
            protocol.response.headers['Access-Control-Allow-Origin'] = protocol.request.origin

            if self._app.cors.methods:
                protocol.response.headers['Access-Control-Allow-Methods'] = ', '.join(self._app.cors.methods - self._app.cors.exclude_methods)

            if self._app.cors.headers == '*':
                protocol.response.headers['Access-Control-Allow-Headers'] = self._app.cors.headers
            elif self._app.cors.headers:
                protocol.response.headers['Access-Control-Allow-Headers'] = ', '.join(self._app.cors.headers)

        try:
            content, streamed = await protocol.response()
            protocol.transport.write(content)
            while streamed:
                content, streamed = await protocol.response()
                protocol.transport.write(content)
        except RuntimeError:
            ...

        if not recycled:
            await self.http_afterResponse(protocol)
            if self._app.signal.http_afterResponse.receivers:
                await self._app.signal.http_afterResponse.send_async(**{
                    'request': protocol.request,
                    'response': protocol.response,
                    **protocol.kwargs
                })

    async def noResponse(self, protocol: 'HttpProtocol') -> BaseResponse:
        protocol.response = Response(status = http.HTTPStatus.INTERNAL_SERVER_ERROR)

    async def http_beforeResponse(self, protocol: 'HttpProtocol') -> BaseResponse | None:
        ...

    async def http_afterResponse(self, protocol: 'HttpProtocol'):
        for text in self._app._text.http(protocol):
            logger.http(text[0], text[1])

    async def websocket_request(self, protocol: 'WebsocketProtocol'):
        try:
            try:
                Server, kwargs = self._app.routeBus._match(protocol.request.path, 'WEBSOCKET')
                protocol.kwargs.update(kwargs)
            except KeyError as e:
                await self.websocket_afterRequest(protocol)
                if self._app.signal.websocket_afterRequest.receivers:
                    await self._app.signal.websocket_afterRequest.send_async(**{
                        'request': protocol.request,
                        **protocol.kwargs
                    })

                if e.args[0] == 0:
                    await self.websocket_404(protocol)
                    if self._app.signal.websocket_404.receivers:
                        await self._app.signal.websocket_404.send_async(**{
                            'request': protocol.request,
                            'response': protocol.response,
                            **protocol.kwargs
                        })
                    return await self.websocket_response(protocol)

                elif e.args[0] == 1:
                    await self.websocket_405(protocol)
                    if self._app.signal.websocket_405.receivers:
                        await self._app.signal.websocket_405.send_async(**{
                            'request': protocol.request,
                            'response': protocol.response,
                            **protocol.kwargs
                        })
                    return await self.websocket_response(protocol)

                raise e

            protocol.server = Server()

            await self.websocket_afterRequest(protocol)
            if self._app.signal.websocket_afterRequest.receivers:
                await self._app.signal.websocket_afterRequest.send_async(**{
                    'request': protocol.request,
                    **protocol.kwargs
                })

            await self.websocket_subprotocol(protocol)

            return await self.websocket_response(protocol)
        except BaseException as e:
            try:
                await self.websocket_500(protocol, e)
                if self._app.signal.websocket_500.receivers:
                    await self._app.signal.websocket_500.send_async(**{
                        'request': protocol.request,
                        'response': protocol.response,
                        'e': e,
                        **protocol.kwargs
                    })
                await self.websocket_response(protocol)
            except BaseException as e:
                await self.websocket_500(protocol, e, True)
                await self.websocket_response(protocol, True)

    async def websocket_afterRequest(self, protocol: 'WebsocketProtocol'):
        ...

    async def websocket_404(self, protocol: 'WebsocketProtocol'):
        protocol.response = Response(status = http.HTTPStatus.NOT_FOUND)
        del protocol.response.headers['Transfer-Encoding']

    async def websocket_405(self, protocol: 'WebsocketProtocol'):
        protocol.response = Response(status = http.HTTPStatus.METHOD_NOT_ALLOWED)
        del protocol.response.headers['Transfer-Encoding']

    async def websocket_500(self, protocol: 'WebsocketProtocol', e: BaseException, recycled: bool = False, connected: bool = False):
        if not connected:
            protocol.response = Response(status = http.HTTPStatus.INTERNAL_SERVER_ERROR)
            del protocol.response.headers['Transfer-Encoding']

        if not recycled:
            for text in self._app._text.websocket_500(protocol, e):
                logger.danger(text[0], text[1])

    async def websocket_response(self, protocol: 'WebsocketProtocol', recycled: bool = False) -> Tuple[int, Dict[str, str], bytes]:
        if not protocol.response or protocol.response.status == 200:
            return

        if not recycled:
            await self.websocket_beforeResponse(protocol)
            if self._app.signal.websocket_beforeResponse.receivers:
                await self._app.signal.websocket_beforeResponse.send_async(**{
                    'request': protocol.request,
                    'response': protocol.response,
                    **protocol.kwargs
                })

        results = int(protocol.response.status), protocol.response.headers, protocol.response.body.encode()

        if not recycled:
            for text in self._app._text.websocket_response(protocol):
                logger.websocket(text[0], text[1])

            await self.websocket_afterResponse(protocol)
            if self._app.signal.websocket_afterResponse.receivers:
                await self._app.signal.websocket_afterResponse.send_async(**{
                    'request': protocol.request,
                    'response': protocol.response,
                    **protocol.kwargs
                })

        return results

    async def websocket_beforeResponse(self, protocol: 'WebsocketProtocol'):
        ...

    async def websocket_afterResponse(self, protocol: 'WebsocketProtocol'):
        ...

    async def websocket_subprotocol(self, protocol: 'WebsocketProtocol') -> str:
        if not protocol.request.headers.get('Sec-Websocket-Protocol', None):
            return

        protocol.request.subprotocols = protocol.request.headers['Sec-Websocket-Protocol'].split(', ')

        await self.websocket_beforeSubprotocol(protocol)
        if self._app.signal.websocket_beforeSubprotocol.receivers:
            await self._app.signal.websocket_beforeSubprotocol.send_async(**{
                'request': protocol.request,
                **protocol.kwargs
            })

        protocol.request.subprotocol = await protocol.server.subprotocol(**{
            'request': protocol.request,
            **protocol.kwargs
        })
        if protocol.request.subprotocol not in protocol.request.subprotocols:
            protocol.response = Response(status = http.HTTPStatus.BAD_REQUEST)
            del protocol.response.headers['Transfer-Encoding']

        await self.websocket_afterSubprotocol(protocol)
        if self._app.signal.websocket_afterSubprotocol.receivers:
            await self._app.signal.websocket_afterSubprotocol.send_async(**{
                'request': protocol.request,
                'response': protocol.response,
                **protocol.kwargs
            })

    async def websocket_beforeSubprotocol(self, protocol: 'WebsocketProtocol'):
        ...

    async def websocket_afterSubprotocol(self, protocol: 'WebsocketProtocol'):
        ...

    async def websocket(self, protocol: 'WebsocketProtocol'):
        try:
            await self.websocket_beforeConnection(protocol)
            if self._app.signal.websocket_beforeConnection.receivers:
                await self._app.signal.websocket_beforeConnection.send_async(**{
                    'request': protocol.request,
                    **protocol.kwargs
                })

            await self.websocket_connection(protocol)
            await protocol.server.connection(**{
                'request': protocol.request,
                **protocol.kwargs
            })

            await self.websocket_afterConnection(protocol)
            if self._app.signal.websocket_afterConnection.receivers:
                await self._app.signal.websocket_afterConnection.send_async(**{
                    'request': protocol.request,
                    **protocol.kwargs
                })

            try:
                while not protocol.transport.is_closing():
                    await self._app._handle.websocket_message(protocol)
            except asyncio.CancelledError:
                ...

            await self.websocket_disconnection(protocol)
            await self.websocket_afterDisconnection()
            if self._app.signal.websocket_afterDisconnection.receivers:
                await self._app.signal.websocket_afterDisconnection.send_async(**{
                    'request': protocol.request,
                    **protocol.kwargs
                })
        except BaseException as e:
            try:
                await self.websocket_500(protocol, e, False, True)
                if self._app.signal.websocket_500.receivers:
                    await self._app.signal.websocket_500.send_async(**{
                        'request': protocol.request,
                        'response': protocol.response,
                        'e': e,
                        **protocol.kwargs
                    })
            except BaseException as e:
                await self.websocket_500(protocol, e, True, True)

    async def websocket_beforeConnection(self, protocol: 'WebsocketProtocol'):
        ...

    async def websocket_connection(self, protocol: 'WebsocketProtocol'):
        for text in self._app._text.websocket_connection(protocol):
            logger.websocket(text[0], text[1])

    async def websocket_afterConnection(self, protocol: 'WebsocketProtocol'):
        ...

    async def websocket_beforeConnection(self, protocol: 'WebsocketProtocol'):
        ...

    async def websocket_message(self, protocol: 'WebsocketProtocol'):
        try:
            message = await asyncio.wait_for(protocol.recv(), timeout = self._app.server.intervalTime)

            await self.websocket_beforeMessage(protocol, message)
            if self._app.signal.websocket_beforeMessage.receivers:
                await self._app.signal.websocket_beforeMessage.send_async(**{
                    'request': protocol.request,
                    'message': message,
                    **protocol.kwargs
                })

            await protocol.server.message(**{
                'message': message,
                **protocol.kwargs
            })

            await self.websocket_afterMessage(protocol, message)
            if self._app.signal.websocket_afterMessage.receivers:
                await self._app.signal.websocket_afterMessage.send_async({
                    'request': protocol.request,
                    'message': message,
                    **protocol.kwargs
                })
        except (websockets.exceptions.ConnectionClosed, websockets.exceptions.ConnectionClosedError, websockets.exceptions.ConnectionClosedOK, asyncio.TimeoutError):
            ...

    async def websocket_beforeMessage(self, protocol: 'WebsocketProtocol', message: str | bytes):
        ...

    async def websocket_afterMessage(self, protocol: 'WebsocketProtocol', message: str | bytes):
        ...

    async def websocket_send(self, protocol: 'WebsocketProtocol', message: str | bytes):
        await self.websocket_beforeSending(protocol, message)
        if self._app.signal.websocket_beforeSending.receivers:
            await self._app.signal.websocket_beforeSending.send_async(**{
                'request': protocol.request,
                'message': message,
                **protocol.kwargs
            })

        await protocol.send(message)

        await self.websocket_afterSending(protocol, message)
        if self._app.signal.websocket_afterSending.receivers:
            await self._app.signal.websocket_afterSending.send_async(**{
                'request': protocol.request,
                'message': message,
                **protocol.kwargs
            })

    async def websocket_beforeSending(self, protocol: 'WebsocketProtocol', message: str | bytes):
        ...

    async def websocket_afterSending(self, protocol: 'WebsocketProtocol', message: str | bytes):
        ...

    async def websocket_close(self, protocol: 'WebsocketProtocol', code: int, reason: str):
        await self.websocket_beforeClosing(protocol, code, reason)
        if self._app.signal.websocket_beforeClosing.receivers:
            await self._app.signal.websocket_beforeClosing.send_async(**{
                'request': protocol.request,
                'code': code,
                'reason': reason,
                **protocol.kwargs
            })

        await protocol.close(code, reason)

        await self.websocket_afterClosing(protocol, code, reason)
        if self._app.signal.websocket_afterSending.receivers:
            await self._app.signal.websocket_afterSending.send_async(**{
                'request': protocol.request,
                'code': code,
                'reason': reason,
                **protocol.kwargs
            })

    async def websocket_beforeClosing(self, protocol: 'WebsocketProtocol', code: int, reason: str):
        ...

    async def websocket_afterClosing(self, protocol: 'WebsocketProtocol', code: int, reason: str):
        ...

    async def websocket_disconnection(self, protocol: 'WebsocketProtocol'):
        await protocol.server.disconnection(**{
            'request': protocol.request,
            **protocol.kwargs
        })

        for text in self._app._text.websocket_disconnection(protocol):
            logger.websocket(text[0], text[1])

    async def websocket_afterDisconnection(self):
        ...

    async def server_beforeStopping(self):
        ...

    async def worker_beforeStopping(self):
        ...

    def worker_afterStopping(self):
        ...

    def server_afterStopping(self):
        ...
