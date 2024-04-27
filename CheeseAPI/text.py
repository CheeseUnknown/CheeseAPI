import os, time, traceback
from typing import TYPE_CHECKING, List, Tuple, Any

import setproctitle
from CheeseLog import ProgressBar, logger

if TYPE_CHECKING:
    from CheeseAPI.app import App
    from CheeseAPI.protocol import HttpProtocol, WebsocketProtocol

class Text:
    def __init__(self, app: 'App'):
        self._app: 'App' = app
        self.progressBar: ProgressBar = ProgressBar()

        self.response_server: str = 'CheeseAPI'
        self._process_title: str = 'CheeseAPI'
        self.workerProcess_title: str = 'CheeseAPI:Process'
        self.logger: str = '%Y_%m_%d.log'

        setproctitle.setproctitle(self._process_title)

    def server_information(self) -> List[Tuple[str, str]]:
        return [
            (f'The master process {os.getpid()} started', f'The master process <blue>{os.getpid()}</blue> started'),
            (f'''Workspace Information:
Base: {self._app.workspace.base}''' + (f'''
Static: {self._app.workspace.static}''' if self._app.workspace.static and self._app.server.static else '') + (f'''
Log: {self._app.workspace.log}''' if self._app.workspace.log and self._app.workspace.logger else '') + (f'''
Logger: {self._app.workspace.logger}''' if self._app.workspace.log and self._app.workspace.logger else ''), f'''Workspace Information:
Base: <cyan><underline>{self._app.workspace.base}</underline></cyan>''' + (f'''
Static: <cyan><underline>{self._app.workspace.static}</underline></cyan>''' if self._app.workspace.static and self._app.server.static else '') + (f'''
Log: <cyan><underline>{self._app.workspace.log}</underline></cyan>''' if self._app.workspace.log and self._app.workspace.logger else '') + (f'''
Logger: <cyan><underline>{self._app.workspace.logger}</underline></cyan>''' if self._app.workspace.log and self._app.workspace.logger else '')),
            (f'''Server Information:
Host: {self._app.server.host}
Port: {self._app.server.port}
Workers: {self._app.server.workers}
Backlog: {self._app.server.backlog}''' + (f'''
Static: {self._app.server.static}''' if self._app.workspace.static and self._app.server.static else ''), f'''Server Information:
Host: <cyan>{self._app.server.host}</cyan>
Port: <blue>{self._app.server.port}</blue>
Workers: <blue>{self._app.server.workers}</blue>
Backlog: <blue>{self._app.server.backlog}</blue>''' + (f'''
Static: <cyan>{self._app.server.static}</cyan>''' if self._app.workspace.static and self._app.server.static else ''))
        ]

    def loadingModule(self, precent: float, module: str) -> Tuple[str, str]:
        message, styledMessage = self.progressBar(precent)
        return f'Modules: {message} {module}', f'Modules: {styledMessage} {module}'

    def loadedModules(self) -> List[Tuple[str, str]]:
        return [
            (f'''Modules:
''' + ' | '.join(self._app.modules), f'''Modules:
''' + ' | '.join(self._app.modules))
        ]

    def loadingLocalModule(self, precent: float, module: str) -> Tuple[str, str]:
        message, styledMessage = self.progressBar(precent)
        return f'Local Modules: {message} {module}', f'Local Modules: {styledMessage} {module}'

    def loadedLocalModules(self) -> List[Tuple[str, str]]:
        foldernames = self._app.localModules.copy()
        for foldername in self._app.preferred_localModules:
            if foldername in foldernames:
                foldernames.remove(foldername)
                foldernames.insert(0, foldername)
        for foldername in self._app.exclude_localModules:
            if foldername in foldernames:
                foldernames.remove(foldername)

        return [
            (f'''Local Modules:
''' + ' | '.join(foldernames), f'''Local Modules:
''' + ' | '.join(foldernames))
        ]

    def worker_starting(self) -> List[Tuple[str, str]]:
        return [
            (f'''The process {os.getpid()} started''', f'''The process <blue>{os.getpid()}</blue> started''')
        ]

    def server_starting(self) -> List[Tuple[str, str]]:
        return [
            (f'The server started on {self._app.server.host}:{self._app.server.port}', f'The server started on <cyan><underline>{self._app.server.host}:{self._app.server.port}</cyan></underline>')
        ]

    def http(self, protocol: 'HttpProtocol') -> List[Tuple[str, str]]:
        return [
            (f'The {protocol.request.client} accessed {protocol.request.method} {protocol.request.fullPath} and returned {protocol.response.status}', f'The <cyan>{protocol.request.client}</cyan> accessed <cyan>{protocol.request.method} ' + logger.encode(protocol.request.fullPath) + f'</cyan> and returned <blue>{protocol.response.status}</blue>')
        ]

    def http_500(self, protocol: 'HttpProtocol', e: BaseException) -> List[Tuple[str, str]]:
        message = logger.encode(traceback.format_exc()[:-1])
        return [
            (f'''
{message}''', f'''
{message}''')
        ]

    def websocket_response(self, protocol: 'WebsocketProtocol') -> List[Tuple[str, str]]:
        return [
            (f'The {protocol.request.client} accessed {protocol.request.method} {protocol.request.fullPath} and returned {protocol.response.status}', f'The <cyan>{protocol.request.client}</cyan> accessed <cyan>{protocol.request.method} ' + logger.encode(protocol.request.fullPath) + f'</cyan> and returned <blue>{protocol.response.status}</blue>')
        ]

    def websocket_500(self, protocol: 'WebsocketProtocol', e: BaseException) -> List[Tuple[str, str]]:
        message = logger.encode(traceback.format_exc()[:-1])
        return [
            (f'''
{message}''', f'''
{message}''')
        ]

    def websocket_connection(self, protocol: 'WebsocketProtocol') -> List[Tuple[str, str]]:
        return [
            (f'The {protocol.request.client} connected {protocol.request.method} {protocol.request.fullPath}', f'The <cyan>{protocol.request.client}</cyan> connected <cyan>{protocol.request.method} ' + logger.encode(protocol.request.fullPath) + f'</cyan>')
        ]

    def websocket_disconnection(self, protocol: 'WebsocketProtocol') -> List[Tuple[str, str]]:
        return [
            (f'The {protocol.request.client} disconnected {protocol.request.method} {protocol.request.fullPath}', f'The <cyan>{protocol.request.client}</cyan> disconnected <cyan>{protocol.request.method} ' + logger.encode(protocol.request.fullPath) + f'</cyan>')
        ]

    def worker_stopping(self) -> List[Tuple[str, str]]:
        return [
            (f'The process {os.getpid()} stopped', f'The process <blue>{os.getpid()}</blue> stopped')
        ]

    def server_stopping(self) -> List[Tuple[str, str]]:
        timer = time.time() - self._app.g['startTime']
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

        return [
            (message, styledMessage)
        ]

    def validator_requiredMessage(self, scope: str, key: str) -> str:
        return f'参数{scope}.{key}是必要的'

    def validator_typeMessage(self, scope: str, key: str, expected_type: object) -> str:
        return f'参数{scope}.{key}无法转换为{expected_type.__name__}'

    def validator_patternMessage(self, scope: str, key: str) -> str:
        return f'参数{scope}.{key}正则校验错误'

    def validator_minMessage(self, scope: str, key: str, min: object) -> str:
        return f'参数{scope}.{key}不允许小于{min}'

    def validator_maxMessage(self, scope: str, key: str, max: object) -> str:
        return f'参数{scope}.{key}不允许大于{max}'

    def validator_enumMessage(self, scope: str, key: str, enum: List[Any]) -> str:
        return f'参数{scope}.{key}不允许为{enum}之外的值'

    @property
    def process_title(self) -> str:
        return self._process_title

    @process_title.setter
    def process_title(self, value: str):
        self._process_title = value

        setproctitle.setproctitle(self._process_title)
