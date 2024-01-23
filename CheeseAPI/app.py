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
        from CheeseAPI.route import Route
        from CheeseAPI.workspace import Workspace
        from CheeseAPI.cors import Cors

        self.workspace: Workspace = Workspace()
        self.server: Server = Server()
        self.httpWorker: HttpWorker = HttpWorker()
        self.websocketWorker: WebsocketWorker = WebsocketWorker()
        self.route: Route = Route()
        self.cors: Cors = Cors()
        self.managers: Dict[str, multiprocessing.Manager] = {}

        self.modules: List[str] = []
        self.localModules: List[str] | Literal[True] = True
        self.exclude_localModules: List[str] = []
        self.preferred_localModules: List[str] = []

        self.handle: Handle = Handle()
        self.g: Dict[str, Any] = {}

    def run(self, *, managers: Dict[str, multiprocessing.Manager] = {}):
        try:
            self.managers.update(managers)
            manager = multiprocessing.Manager()
            self.managers['lock'] = manager.Lock()
            self.managers['startedWorkerNum'] = manager.Value(int, 0)
            self.managers['firstRequest'] = manager.Value(bool, False)

            self.handle._server_beforeStartingHandle(self)
            for server_beforeStartingHandle in self.handle.server_beforeStartingHandles:
                server_beforeStartingHandle()
            if signal.receiver('server_beforeStartingHandle'):
                signal.send('server_beforeStartingHandle')

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.server.host, self.server.port))
            sock.set_inheritable(True)

            multiprocessing.allow_connection_pickling()
            for i in range(0, self.server.workers - 1):
                process = multiprocessing.Process(target = run, args = (self, sock), name = f'CheeseAPI_Subprocess<{i}>', daemon = True)
                process.start()

            run(self, sock)

            while self.managers['startedWorkerNum'].value != 0:
                time.sleep(0.1)
        except Exception as e:
            sys.excepthook(Exception, e, sys.exc_info()[2])

        if signal.receiver('server_beforeStoppingHandle'):
            signal.send('server_beforeStoppingHandle')
        for server_beforeStoppingHandle in self.handle.server_beforeStoppingHandles:
            server_beforeStoppingHandle()
        self.handle._server_beforeStoppingHandle(self)
        logger.destory()

app = App()

async def _run(app: App, sock: socket.socket):
    from CheeseAPI.protocol import HttpProtocol

    app.handle._worker_beforeStartingHandle()
    for worker_beforeStartingHandle in app.handle.worker_beforeStartingHandles:
        worker_beforeStartingHandle()
    if signal.receiver('worker_beforeStartingHandle'):
        signal.send('worker_beforeStartingHandle')

    HttpProtocol.managers = app.managers

    loop = asyncio.get_running_loop()
    server = await loop.create_server(HttpProtocol, sock = sock)
    loop.add_signal_handler(pySignal.SIGINT, app.handle._exitSignalHandle, server)
    loop.add_signal_handler(pySignal.SIGTERM, app.handle._exitSignalHandle, server)

    for worker_afterStartingHandle in app.handle.worker_afterStartingHandles:
        worker_afterStartingHandle()
    if signal.receiver('worker_afterStartingHandle'):
        signal.send('worker_afterStartingHandle')

    with app.managers['lock']:
        app.managers['startedWorkerNum'].value += 1
        if app.managers['startedWorkerNum'].value == app.server.workers:
            app.handle._server_afterStartingHandle(app)
            for server_afterStartingHandle in app.handle.server_afterStartingHandles:
                server_afterStartingHandle()
            if signal.receiver('server_afterStartingHandle'):
                signal.send('server_afterStartingHandle')

    while server.is_serving():
        await asyncio.sleep(0.1)

    if signal.receiver('worker_beforeStoppingHandle'):
        signal.send('worker_beforeStoppingHandle')
    for worker_beforeStoppingHandle in app.handle.worker_beforeStoppingHandles:
        worker_beforeStoppingHandle()
    app.handle._worker_beforeStoppingHandle(app)

    with app.managers['lock']:
        app.managers['startedWorkerNum'].value -= 1

def run(app, sock):
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(_run(app, sock))
