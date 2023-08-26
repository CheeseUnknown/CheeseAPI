import asyncio, multiprocessing, socket, time
import signal as pySignal
from typing import Dict, Any, List, Literal

import uvloop
from CheeseLog import logger

from CheeseAPI import exception
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

        self.modules: List[str] = []
        self.localModules: List[str] | Literal[True] = True

        self.handle: Handle = Handle()
        self.g: Dict[str, Any] = {}

    def run(self, *, managers: Dict[str, multiprocessing.Manager] = {}):
        manager = multiprocessing.Manager()
        managers['lock'] = manager.Lock()
        managers['startedWorkerNum'] = manager.Value(int, 0)
        managers['firstRequest'] = manager.Value(bool, False)

        self.handle._server_beforeStartingHandle()
        for server_beforeStartingHandle in self.handle.server_beforeStartingHandles:
            server_beforeStartingHandle()
        if signal.receiver('server_beforeStartingHandle'):
            signal.send('server_beforeStartingHandle')

        sock = socket.socket(socket.AF_INET)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.server.host, self.server.port))
        sock.set_inheritable(True)

        for i in range(0, self.server.workers - 1):
            process = multiprocessing.Process(target = run, args = (app, sock, managers), name = f'CheeseAPI_Subprocess<{i}>', daemon = True)
            process.start()

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        asyncio.run(_run(app, sock, managers))

        while managers['startedWorkerNum'].value != 0:
            time.sleep(0.1)
        logger.destory()

app = App()

async def _run(app: App, sock: socket.socket, managers):
    from CheeseAPI.protocol import HttpProtocol

    app.handle._worker_beforeStartingHandle()
    for worker_beforeStartingHandle in app.handle.worker_beforeStartingHandles:
        worker_beforeStartingHandle()
    if signal.receiver('worker_beforeStartingHandle'):
        signal.send('worker_beforeStartingHandle')

    HttpProtocol.managers = managers

    loop = asyncio.get_running_loop()
    server = await loop.create_server(HttpProtocol, sock = sock)
    loop.add_signal_handler(pySignal.SIGINT, app.handle._exitSignalHandle, server)
    loop.add_signal_handler(pySignal.SIGTERM, app.handle._exitSignalHandle, server)

    for worker_afterStartingHandle in app.handle.worker_afterStartingHandles:
        worker_afterStartingHandle()
    if signal.receiver('worker_afterStartingHandle'):
        signal.send('worker_afterStartingHandle')

    with managers['lock']:
        managers['startedWorkerNum'].value += 1
        if managers['startedWorkerNum'].value == app.server.workers:
            app.handle._server_afterStartingHandle()
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
    app.handle._worker_beforeStoppingHandle()

    with managers['lock']:
        managers['startedWorkerNum'].value -= 1
        if managers['startedWorkerNum'].value == 0:
            if signal.receiver('server_beforeStoppingHandle'):
                signal.send('server_beforeStoppingHandle')
            for server_beforeStoppingHandle in app.handle.server_beforeStoppingHandles:
                server_beforeStoppingHandle()
            app.handle._server_beforeStoppingHandle()

def run(app, sock, managers):
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(_run(app, sock, managers))
