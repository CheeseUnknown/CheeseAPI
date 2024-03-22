import multiprocessing, os
from typing import Dict, Any, List

from CheeseAPI.text import Text
from CheeseAPI.server import Server
from CheeseAPI.workspace import Workspace
from CheeseAPI.handle import Handle
from CheeseAPI.signal import _Signal
from CheeseAPI.route import Route, RouteBus
from CheeseAPI.cors import Cors

class App:
    def __init__(self):
        self.server: Server = Server(self)
        self.workspace: Workspace = Workspace(self)
        self.signal: _Signal = _Signal(self)
        self.managers: Dict[str, Any] = {}
        self.g: Dict[str, Any] = {
            'startTime': None
        }
        self.route: Route = Route()
        self.routeBus: RouteBus = RouteBus()
        self.cors: Cors = Cors()

        self.modules: List[str] = []
        self.localModules: List[str] = []
        self.exclude_localModules: List[str] = []
        self.preferred_localModules: List[str] = []

        self._text: Text = Text(self)
        self._managers: Dict[str, Any] = {
            'server.workers': multiprocessing.Value('i', 0),
            'lock': multiprocessing.Lock()
        }
        self._handle: Handle = Handle(self)

        # 初始化本地模块
        for foldername in os.listdir(self.workspace.base):
            if foldername[0] == '.' or foldername == '__pycache__':
                continue

            folderPath = os.path.join(self.workspace.base, foldername)
            if not os.path.isdir(folderPath):
                continue

            staticPath = os.path.join(self.workspace.base, self.workspace.static)
            if self.workspace.static and os.path.exists(staticPath) and os.path.samefile(folderPath, staticPath):
                continue

            logPath = os.path.join(self.workspace.base, self.workspace.log)
            if self.workspace.log and os.path.exists(logPath) and os.path.samefile(folderPath, logPath):
                continue

            self.localModules.append(foldername)

    def run(self):
        self._handle.server_start()

app: App = App()
