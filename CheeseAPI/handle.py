from http import HTTPMethod, HTTPStatus
from typing import TYPE_CHECKING, Dict, Tuple
from time import time
from os.path import dirname, join, isfile, isdir
from inspect import getfile
from os import listdir, killpg, getpid
from ipaddress import IPv4Address, AddressValueError
from socket import socket, AF_INET, SOCK_STREAM, AF_INET6, SOL_SOCKET, SO_REUSEADDR
from multiprocessing import allow_connection_pickling, Process, Queue
from traceback import format_exc
from signal import SIGKILL, SIGINT, SIGTERM
from gc import disable, enable
from asyncio import set_event_loop_policy, run, get_running_loop, sleep, CancelledError, wait_for, TimeoutError, gather

import uvloop
from CheeseLog import logger
from setproctitle import setproctitle, getproctitle
from websockets.exceptions import ConnectionClosed

from CheeseAPI.response import BaseResponse, FileResponse, Response
from CheeseAPI.exception import Route_404_Exception, Route_405_Exception
from CheeseAPI.websocket import WebsocketServer

if TYPE_CHECKING:
    from CheeseAPI.app import App
    from CheeseAPI.protocol import HttpProtocol, WebsocketProtocol
    from CheeseAPI.schedule import ScheduleTask

logger_starting = logger.starting
FROMLIST = ['']
logger_loading = logger.loading
logger_loaded = logger.loaded
logger_error = logger.error
logger_encode = logger.encode
logger_debug = logger.debug
HTTP_METHOD_OPTIONS = HTTPMethod.OPTIONS
HTTP_METHOD_GET = HTTPMethod.GET
HTTP_STATUS_OK = HTTPStatus.OK
HTTP_STATUS_NOT_FOUND = HTTPStatus.NOT_FOUND
HTTP_STATUS_METHOD_NOT_ALLOWED = HTTPStatus.METHOD_NOT_ALLOWED
HTTP_STATUS_INTERNAL_SERVER_ERROR = HTTPStatus.INTERNAL_SERVER_ERROR
HTTP_STATUS_BAD_REQUEST = HTTPStatus.BAD_REQUEST
STATIC_INDEX_FILE_NAMES = ('', '.html', 'index.html', '/index.html')
STATIC_EXCEPTIONS = (FileNotFoundError, NotADirectoryError, IsADirectoryError)
logger_danger = logger.danger
WEBSOCKET_EXCEPTIONS = (ConnectionClosed, TimeoutError)

class Handle:
    def __init__(self, app: 'App'):
        self._app: 'App' = app

    def server_beforeStarting(self):
        self._app.g['startTime'] = time()

        for text in self._app._text.server_information():
            logger_starting(text[0], text[1])

        self.loadModules()
        self.loadLocalModules()

    def loadModule(self, name: str):
        module = __import__(name)
        module_type = getattr(module, 'CheeseAPI_module_type', 'single')
        module_dependencies = getattr(module, 'CheeseAPI_module_dependencies', [])
        module_dependencies.reverse()
        module_preferredSubModules = getattr(module, 'CheeseAPI_module_preferredSubModules', [])
        module_preferredSubModules.reverse()
        module_workspace_static = getattr(module, 'CheeseAPI_module_workspace_static', None)
        module_server_static = getattr(module, 'CheeseAPI_module_server_static', None)

        # 依赖
        if module_dependencies:
            for dependency in module_dependencies:
                self.loadModule(dependency)

        modulePath = dirname(getfile(module))

        # 静态文件
        if module_workspace_static and module_server_static:
            self._app.workspace._module_static.append(join(modulePath, module_workspace_static))
            self._app.server._module_static.append(module_server_static)

        # 单模块
        if module_type == 'single':
            for filename in listdir(modulePath):
                if isfile(join(modulePath, filename)) and filename.endswith('.py'):
                    __import__(f'{name}.{filename[:-3]}', fromlist = FROMLIST)
        # 多模块
        elif module_type == 'multiple':
            foldernames = listdir(modulePath)
            for foldername in module_preferredSubModules:
                if foldername in foldernames:
                    foldernames.remove(foldername)
                foldernames.insert(0, foldername)

            for foldername in foldernames:
                if foldername == '__pycache__':
                    continue

                folderPath = join(modulePath, foldername)
                if isdir(folderPath):
                    for filename in listdir(folderPath):
                        if isfile(join(folderPath, filename)) and filename.endswith('.py'):
                            __import__(f'{name}.{foldername}.{filename[:-3]}', fromlist = FROMLIST)

    def loadModules(self):
        moduleNum = len(self._app.modules)
        if moduleNum:
            print()

            for i in range(moduleNum):
                logger_loading(*self._app._text.loadingModule(i / moduleNum, self._app.modules[i]))

                self.loadModule(self._app.modules[i])

            for text in self._app._text.loadedModules():
                logger_loaded(text[0], text[1], refreshed = True)

    def loadLocalModule(self, name: str):
        modulePath = join(self._app.workspace.base, name)
        for filename in listdir(modulePath):
            if isfile(join(modulePath, filename)) and filename.endswith('.py'):
                __import__(f'{name}.{filename[:-3]}', fromlist = FROMLIST)

    def loadLocalModules(self):
        foldernames = self._app.localModules.copy()
        for foldername in reversed(self._app.preferred_localModules):
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
                logger_loading(message, styledMessage)

                self.loadLocalModule(foldernames[i])

            for text in self._app._text.loadedLocalModules():
                logger_loaded(text[0], text[1], refreshed = True)

    def server_start(self):
        try:
            self._app._handle.server_beforeStarting()
            self._app.signal.server_beforeStarting.send()

            try:
                IPv4Address(self._app.server.host)
                sock = socket(AF_INET, SOCK_STREAM)
            except AddressValueError:
                sock = socket(AF_INET6, SOCK_STREAM)
            sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            sock.bind((self._app.server.host, self._app.server.port))
            sock.listen(self._app.server.backlog)
            sock.set_inheritable(True)

            allow_connection_pickling()
            processes: Tuple[Process] = tuple(Process(target = self.worker_start, args = (sock,), name = self._app._text.workerProcess_title) for i in range(self._app.server.workers - 1))
            for process in processes:
                process.start()

            self.worker_start(sock, True)

            for process in processes:
                process.terminate()
                process.join()

            for text in self._app._text.server_stopping():
                logger.ending(text[0], text[1])

            self.server_afterStopping()
            self._app.signal.server_afterStopping.send()
        except KeyboardInterrupt:
            ...
        except:
            logger_error(f'''
{logger_encode(format_exc()[:-1])}''')
        finally:
            killpg(getpid(), SIGKILL)

    def worker_beforeStarting(self):
        for text in self._app._text.worker_starting():
            logger_debug(text[0], text[1])

    def worker_start(self, sock, master: bool = False):
        try:
            if not master:
                setproctitle(self._app._text.workerProcess_title)

            self.worker_beforeStarting()
            self._app.signal.worker_beforeStarting.send()

            set_event_loop_policy(uvloop.EventLoopPolicy())
            run(self.worker_run(sock, master))

            with self._app._managers_['lock']:
                self._app._managers_['server.workers'].value -= 1

                for text in self._app._text.worker_stopping():
                    logger_debug(text[0], text[1])

                self.worker_afterStopping()
                self._app.signal.worker_afterStopping.send()
        except:
            logger_error(f'''The process {getpid()} stopped
{logger_encode(format_exc()[:-1])}''', f'''The process <blue>{getpid()}</blue> stopped
{logger_encode(format_exc()[:-1])}''')

    async def worker_run(self, sock, master: bool):
        from CheeseAPI.app import app
        from CheeseAPI.protocol import HttpProtocol

        app._g = self._app.g
        app._managers = self._app.managers
        app._managers_ = self._app._managers_

        loop = get_running_loop()
        server = await loop.create_server(HttpProtocol, sock = sock)
        loop.add_signal_handler(SIGINT, lambda server: server.close(), server)
        loop.add_signal_handler(SIGTERM, lambda server: server.close(), server)

        await self.worker_afterStarting()
        await self._app.signal.worker_afterStarting.async_send()

        with self._app._managers_['lock']:
            self._app._managers_['server.workers'].value += 1
            if self._app._managers_['server.workers'].value == self._app.server.workers:
                for text in self._app._text.server_starting():
                    logger_starting(text[0], text[1])

                await self.server_afterStarting()
                await self._app.signal.server_afterStarting.async_send()

        while server.is_serving():
            timer = time()
            disable()

            if master:
                await self.server_running()
                await self._app.signal.server_running.async_send()

            await self.worker_running()
            await self._app.signal.worker_running.async_send()

            enable()
            await sleep(max(self._app.server.intervalTime - time() + timer, 0))

        with self._app._managers_['lock']:
            if self._app._managers_['server.workers'].value == self._app.server.workers:
                await self.server_beforeStopping()
                await self._app.signal.server_beforeStopping.async_send()

            await self.worker_beforeStopping()
            await self._app.signal.worker_beforeStopping.async_send()

    async def worker_afterStarting(self):
        ...

    async def server_afterStarting(self):
        ...

    async def server_running(self):
        taskKeys = tuple(self._app.scheduler.tasks)
        taskHandleKeys = tuple(self._app.scheduler._taskHandlers)
        for key in taskHandleKeys:
            if key not in taskKeys or not self._app.scheduler._taskHandlers[key].is_alive():
                del self._app.scheduler._taskHandlers[key]
                del self._app.scheduler._queues[key]
                self._app.scheduler.remove(key)

        taskKeys = [key for key in self._app.scheduler.tasks if key not in taskHandleKeys]
        if taskKeys:
            queues = {
                key: (Queue(), Queue()) for key in taskKeys
            }
            taskHandles = {
                key: Process(target = self._app.scheduler._processHandle, args = (key, queues[key]), name = f'{getproctitle()}:SchedulerTask:{key}', daemon = True) for key in taskKeys
            }

            self._app.scheduler._queues.update(queues)
            self._app.scheduler._taskHandlers.update(taskHandles)

            for key in taskKeys:
                self._app.scheduler._taskHandlers[key].start()

        tasks = [self._app.scheduler._taskHandle(key) for key in self._app.scheduler._queues]
        if tasks:
            await gather(*tasks)

    async def worker_running(self):
        ...

    async def http_beforeRequest(self, protocol: 'HttpProtocol'):
        ...

    async def http_afterRequest(self, protocol: 'HttpProtocol'):
        ...

    async def http(self, protocol: 'HttpProtocol'):
        try:
            await self._app._handle.http_beforeRequest(self)
            await self._app.signal.http_beforeRequest.async_send()

            await self.http_static(protocol)
            if isinstance(protocol.response, BaseResponse):
                await self._app.signal.http_static.async_send(**{
                    'request': protocol.request,
                    'response': protocol.response,
                    **protocol.kwargs
                })
                await self.http_response(protocol)
                return

            try:
                fn, protocol.kwargs = self._app.routeBus._match(protocol.request.path, protocol.request.method)
            except Route_404_Exception as e:
                await self.http_afterRequest(protocol)
                await self._app.signal.http_afterRequest.async_send(**{
                    'request': protocol.request,
                    **protocol.kwargs
                })

                await self.http_404(protocol)
                await self._app.signal.http_404.async_send(**{
                    'request': protocol.request,
                    'response': protocol.response,
                    **protocol.kwargs
                })
                await self.http_response(protocol)
                return
            except Route_405_Exception as e:
                await self.http_afterRequest(protocol)
                await self._app.signal.http_afterRequest.async_send(**{
                    'request': protocol.request,
                    **protocol.kwargs
                })

                if protocol.request.method == HTTP_METHOD_OPTIONS:
                    protocol.response = Response(status = 200)

                    await self._app.signal.http_options.async_send(**{
                        'request': protocol.request,
                        'response': protocol.response,
                        **protocol.kwargs
                    })
                    await self.http_response(protocol)
                    return

                await self.http_405(protocol)
                await self._app.signal.http_405.async_send(**{
                    'request': protocol.request,
                    'response': protocol.response,
                    'e': e,
                    **protocol.kwargs
                })
                await self.http_response(protocol)
                return

            await self.http_afterRequest(protocol)
            await self._app.signal.http_afterRequest.async_send(**{
                'request': protocol.request,
                **protocol.kwargs
            })

            protocol.response = await fn(**{
                'request': protocol.request,
                **protocol.kwargs
            })

            await self._app.signal.http_custom.async_send(**{
                'request': protocol.request,
                'response': protocol.response,
                **protocol.kwargs
            })

            await self.http_response(protocol)
        except Exception as e:
            try:
                await self.http_500(protocol, e)
                await self._app.signal.http_500.async_send(**{
                    'request': protocol.request,
                    'response': protocol.response,
                    'e': e,
                    **protocol.kwargs
                })
                await self.http_response(protocol)
            except Exception as e:
                await self.http_500(protocol, e, True)
                await self.http_response(protocol, True)

    async def http_static(self, protocol: 'HttpProtocol'):
        if protocol.request.method == HTTP_METHOD_GET:
            for i in range(len(self._app.workspace._module_static) + 1):
                if protocol.response:
                    break

                if i == 0:
                    server_static = self._app.server.static
                    workspace_static = self._app.workspace.static
                    if not server_static or not workspace_static:
                        continue
                else:
                    server_static = self._app.server._module_static[i - 1]
                    workspace_static = self._app.workspace._module_static[i - 1]

                if server_static and workspace_static and protocol.request.path.startswith(server_static):
                    for key in STATIC_INDEX_FILE_NAMES:
                        try:
                            protocol.response = FileResponse(join(self._app.workspace.static, protocol.request.path[1:] + key))

                            await self.http_afterRequest(protocol)
                            await self._app.signal.http_afterRequest.async_send(**{
                                'request': protocol.request,
                                **protocol.kwargs
                            })

                            await self._app.signal.http_static.async_send(**{
                                'request': protocol.request,
                                **protocol.kwargs
                            })

                            break
                        except STATIC_EXCEPTIONS:
                            ...

    async def http_options(self, protocol: 'HttpProtocol'):
        protocol.response = Response(status = HTTP_STATUS_OK)

    async def http_404(self, protocol: 'HttpProtocol'):
        protocol.response = Response(status = HTTP_STATUS_NOT_FOUND)

    async def http_405(self, protocol: 'HttpProtocol'):
        protocol.response = Response(status = HTTP_STATUS_METHOD_NOT_ALLOWED)

    async def http_500(self, protocol: 'HttpProtocol', e: BaseException, recycled: bool = False):
        protocol.response = Response(status = HTTP_STATUS_INTERNAL_SERVER_ERROR)

        if not recycled:
            for text in self._app._text.http_500(protocol, e):
                logger_danger(text[0], text[1])

    async def http_response(self, protocol: 'HttpProtocol', recycled: bool = False):
        if not isinstance(protocol.response, BaseResponse):
            await self.noResponse(protocol)

        if not recycled:
            await self.http_beforeResponse(protocol)
            await self._app.signal.http_beforeResponse.async_send(**{
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
            await self._app.signal.http_afterResponse.async_send(**{
                'request': protocol.request,
                'response': protocol.response,
                **protocol.kwargs
            })

    async def noResponse(self, protocol: 'HttpProtocol') -> BaseResponse:
        protocol.response = Response(status = HTTP_STATUS_INTERNAL_SERVER_ERROR)

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
            except Route_404_Exception as e:
                await self.websocket_afterRequest(protocol)
                await self._app.signal.websocket_afterRequest.async_send(**{
                    'request': protocol.request,
                    **protocol.kwargs
                })

                await self.websocket_404(protocol)
                await self._app.signal.websocket_404.async_send(**{
                    'request': protocol.request,
                    'response': protocol.response,
                    **protocol.kwargs
                })
                return await self.websocket_response(protocol)
            except Route_405_Exception as e:
                await self.websocket_afterRequest(protocol)
                await self._app.signal.websocket_afterRequest.async_send(**{
                    'request': protocol.request,
                    **protocol.kwargs
                })

                await self.websocket_405(protocol)
                await self._app.signal.websocket_405.async_send(**{
                    'request': protocol.request,
                    'response': protocol.response,
                    **protocol.kwargs
                })
                return await self.websocket_response(protocol)

            protocol.server = Server()

            await self.websocket_afterRequest(protocol)
            await self._app.signal.websocket_afterRequest.async_send(**{
                'request': protocol.request,
                **protocol.kwargs
            })

            await self.websocket_subprotocol(protocol)

            return await self.websocket_response(protocol)
        except BaseException as e:
            try:
                await self.websocket_500(protocol, e)
                await self._app.signal.websocket_500.async_send(**{
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
        protocol.response = Response(status = HTTP_STATUS_NOT_FOUND)
        del protocol.response.headers['Transfer-Encoding']

    async def websocket_405(self, protocol: 'WebsocketProtocol'):
        protocol.response = Response(status = HTTP_STATUS_METHOD_NOT_ALLOWED)
        del protocol.response.headers['Transfer-Encoding']

    async def websocket_500(self, protocol: 'WebsocketProtocol', e: BaseException, recycled: bool = False, connected: bool = False):
        if not connected:
            protocol.response = Response(status = HTTP_STATUS_INTERNAL_SERVER_ERROR)
            del protocol.response.headers['Transfer-Encoding']

        if not recycled:
            for text in self._app._text.websocket_500(protocol, e):
                logger_danger(text[0], text[1])

    async def websocket_response(self, protocol: 'WebsocketProtocol', recycled: bool = False) -> Tuple[int, Dict[str, str], bytes]:
        if not protocol.response or protocol.response.status == 200:
            return

        if not recycled:
            await self.websocket_beforeResponse(protocol)
            await self._app.signal.websocket_beforeResponse.async_send(**{
                'request': protocol.request,
                'response': protocol.response,
                **protocol.kwargs
            })

        results = int(protocol.response.status), protocol.response.headers, protocol.response.body.encode()

        if not recycled:
            for text in self._app._text.websocket_response(protocol):
                logger.websocket(text[0], text[1])

            await self.websocket_afterResponse(protocol)
            await self._app.signal.websocket_afterResponse.async_send(**{
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
        if not protocol.request.headers.get('Sec-Websocket-Protocol', None) and protocol.server.__class__.subprotocol is WebsocketServer.subprotocol:
            return

        protocol.request._subprotocols = protocol.request.headers.get('Sec-Websocket-Protocol', '').split(', ')

        await self.websocket_beforeSubprotocol(protocol)
        await self._app.signal.websocket_beforeSubprotocol.async_send(**{
            'request': protocol.request,
            **protocol.kwargs
        })

        protocol.request._subprotocol = await protocol.server.subprotocol(**{
            'request': protocol.request,
            **protocol.kwargs
        })
        if protocol.request.subprotocol not in protocol.request.subprotocols:
            protocol.response = Response(status = HTTP_STATUS_BAD_REQUEST)
            del protocol.response.headers['Transfer-Encoding']

        await self.websocket_afterSubprotocol(protocol)
        await self._app.signal.websocket_afterSubprotocol.async_send(**{
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
            await self._app.signal.websocket_beforeConnection.async_send(**{
                'request': protocol.request,
                **protocol.kwargs
            })

            await self.websocket_connection(protocol)
            await protocol.server.connection(**{
                'request': protocol.request,
                **protocol.kwargs
            })

            await self.websocket_afterConnection(protocol)
            await self._app.signal.websocket_afterConnection.async_send(**{
                'request': protocol.request,
                **protocol.kwargs
            })

            try:
                while not protocol.transport.is_closing():
                    await self._app._handle.websocket_message(protocol)
            except CancelledError:
                ...

            await self.websocket_disconnection(protocol)
            await self.websocket_afterDisconnection()
            await self._app.signal.websocket_afterDisconnection.async_send(**{
                'request': protocol.request,
                **protocol.kwargs
            })
        except BaseException as e:
            try:
                await self.websocket_500(protocol, e, False, True)
                await self._app.signal.websocket_500.async_send(**{
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
            message = await wait_for(protocol.recv(), timeout = self._app.server.intervalTime)

            await self.websocket_beforeMessage(protocol, message)
            await self._app.signal.websocket_beforeMessage.async_send(**{
                'request': protocol.request,
                'message': message,
                **protocol.kwargs
            })

            await protocol.server.message(**{
                'request': protocol.request,
                'message': message,
                **protocol.kwargs
            })

            await self.websocket_afterMessage(protocol, message)
            await self._app.signal.websocket_afterMessage.async_send({
                'request': protocol.request,
                'message': message,
                **protocol.kwargs
            })
        except WEBSOCKET_EXCEPTIONS:
            ...

    async def websocket_beforeMessage(self, protocol: 'WebsocketProtocol', message: str | bytes):
        ...

    async def websocket_afterMessage(self, protocol: 'WebsocketProtocol', message: str | bytes):
        ...

    async def websocket_send(self, protocol: 'WebsocketProtocol', message: str | bytes):
        await self.websocket_beforeSending(protocol, message)
        await self._app.signal.websocket_beforeSending.async_send(**{
            'request': protocol.request,
            'message': message,
            **protocol.kwargs
        })

        await protocol.send(message)

        await self.websocket_afterSending(protocol, message)
        await self._app.signal.websocket_afterSending.async_send(**{
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
        await self._app.signal.websocket_beforeClosing.async_send(**{
            'request': protocol.request,
            'code': code,
            'reason': reason,
            **protocol.kwargs
        })

        await protocol.close(code, reason)

        await self.websocket_afterClosing(protocol, code, reason)
        await self._app.signal.websocket_afterSending.async_send(**{
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

    async def scheduler_beforeRunning(self, task: 'ScheduleTask'):
        ...

    async def scheduler_afterRunning(self, task: 'ScheduleTask'):
        ...
