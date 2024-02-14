import asyncio, multiprocessing, socket, time, sys
import signal as pySignal
from typing import Dict, Any, List, Literal

import uvloop
from CheeseLog import logger

from CheeseAPI.signal import signal

class App:
    def __init__(self):
        from CheeseAPI.server import Server
        from CheeseAPI.handle import Handle
        from CheeseAPI.worker import HttpWorker, WebsocketWorker
        from CheeseAPI.route import Route, RouteBus
        from CheeseAPI.workspace import Workspace
        from CheeseAPI.cors import Cors

        self.workspace: Workspace = Workspace()
        self.server: Server = Server()
        self.routeBus: RouteBus = RouteBus()
        self.route: Route = Route()
        self.cors: Cors = Cors()
        self.g: Dict[str, Any] = {}
        self.managers: Dict[str, Any] = {
            'lock': multiprocessing.Lock()
        }

        self.modules: List[str] = []
        self.localModules: List[str] | Literal[True] = True
        self.exclude_localModules: List[str] = []
        self.preferred_localModules: List[str] = []

        self.httpWorker: HttpWorker = HttpWorker()
        self.websocketWorker: WebsocketWorker = WebsocketWorker()
        self._handle: Handle = Handle()
        self._managers: Dict[str, Any] = {
            'firstRequest': multiprocessing.Value('b', False),
            'startedWorkerNum': multiprocessing.Value('i', 0)
        }

    def init(self):
        try:
            self._handle._initHandle(self)
        except Exception as e:
            sys.excepthook(Exception, e, sys.exc_info()[2])

    def run(self, *, managers: Dict[str, Any] = {}):
        if 'startTimer' not in app.g:
            logger.error('The app has not yet been initiated')
        else:
            try:
                self.managers.update(managers)
                manager = multiprocessing.Manager()
                self._managers['workspace.logger'] = manager.Value(str, self.workspace.logger)

                self._handle._server_beforeStartingHandle(self)
                if signal.receiver('server_beforeStartingHandle'):
                    signal.send('server_beforeStartingHandle')

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind((self.server.host, self.server.port))
                sock.listen(self.server.backlog)
                sock.set_inheritable(True)

                multiprocessing.allow_connection_pickling()
                for i in range(0, self.server.workers - 1):
                    process = multiprocessing.Process(target = run, args = (self, sock), name = f'CheeseAPI_subprocess')
                    process.start()

                run(self, sock, True)

                while self._managers['startedWorkerNum'].value != 0:
                    time.sleep(0.01)
            except Exception as e:
                sys.excepthook(Exception, e, sys.exc_info()[2])

        if signal.receiver('server_beforeStoppingHandle'):
            signal.send('server_beforeStoppingHandle')
        self._handle._server_beforeStoppingHandle(self)
        logger.destroy()

app = App()

async def _run(_app: App, sock: socket.socket):
    from CheeseAPI.protocol import HttpProtocol

    app.g = _app.g
    app.managers = _app.managers
    app._managers = _app._managers

    app.workspace.logger = app._managers['workspace.logger'].value

    app._handle._worker_beforeStartingHandle()
    if signal.receiver('worker_beforeStartingHandle'):
        await signal.async_send('worker_beforeStartingHandle')

    HttpProtocol.managers = app._managers

    loop = asyncio.get_running_loop()
    server = await loop.create_server(HttpProtocol, sock = sock)
    loop.add_signal_handler(pySignal.SIGINT, app._handle._exitSignalHandle, server)
    loop.add_signal_handler(pySignal.SIGTERM, app._handle._exitSignalHandle, server)

    if signal.receiver('worker_afterStartingHandle'):
        await signal.async_send('worker_afterStartingHandle')

    with app.managers['lock']:
        app._managers['startedWorkerNum'].value += 1
        if app._managers['startedWorkerNum'].value == app.server.workers:
            app._handle._server_afterStartingHandle(app)
            if signal.receiver('server_afterStartingHandle'):
                await signal.async_send('server_afterStartingHandle')

    while server.is_serving():
        if app._managers['workspace.logger'].value != app.workspace.logger:
            app.workspace._logger = app._managers['workspace.logger'].value

        await asyncio.sleep(0.01)

    if signal.receiver('worker_beforeStoppingHandle'):
        await signal.async_send('worker_beforeStoppingHandle')
    app._handle._worker_beforeStoppingHandle(app)

    with app.managers['lock']:
        app._managers['startedWorkerNum'].value -= 1

def run(app, sock, master: bool = False):
    import setproctitle
    setproctitle.setproctitle('CheeseAPI_masterProcess' if master else 'CheeseAPI_subprocess')

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(_run(app, sock))
