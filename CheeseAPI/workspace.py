import os, sys

from typing import TYPE_CHECKING, List

from CheeseLog import logger

if TYPE_CHECKING:
    from CheeseAPI.app import App

class Workspace:
    def __init__(self, app: 'App'):
        self._app: 'App' = app

        self._base: str = os.getcwd()
        self._static: str = './static/'
        self._module_static: List[str] = []
        self._log: str = './logs/'
        self._logger: str = ''
        self.key_file: str | None = None
        self.cert_file: str | None = None

    @property
    def base(self) -> str:
        '''
        工作区的基础路径，后续所有操作都将基于该工作区。
        '''

        return self._base

    @base.setter
    def base(self, value: str):
        self._base = value
        sys.path.append(self._base)

        # 初始化本地模块
        self._app.localModules.clear()
        for foldername in os.listdir(self.base):
            if foldername[0] == '.' or foldername == '__pycache__':
                continue

            folderPath = os.path.join(self.base, foldername)
            if not os.path.isdir(folderPath):
                continue

            staticPath = os.path.join(self.base, self.static)
            if self.static and os.path.exists(staticPath) and os.path.samefile(folderPath, staticPath):
                continue

            logPath = os.path.join(self.base, self.log)
            if self.log and os.path.exists(logPath) and os.path.samefile(folderPath, logPath):
                continue

            self._app.localModules.append(foldername)

    @property
    def static(self) -> str:
        '''
        工作区中静态文件的存放路径；若`app.server.static and app.workspace.static`为`False`，则不开启静态资源功能。
        '''

        return self._static

    @static.setter
    def static(self, value: str):
        self._static = value

    @property
    def log(self) -> str:
        '''
        工作区中日志文件的存放路径；若`app.workspace.log and app.workspace.logger`为`False`，则不输出日志文件。
        '''

        return self._log

    @log.setter
    def log(self, value: str):
        self._log = value

        if self.log and self.logger:
            logger.filePath = os.path.join(self.base, self.log, self.logger)
        else:
            logger.filePath = ''

    @property
    def logger(self) -> str:
        return self._logger

    @logger.setter
    def logger(self, value: str | bool):
        '''
        当前日志文件名；支持时间模板，会在服务器运行的时候自动转换；若`app.workspace.log and app.workspace.logger`为`False`，则不输出日志文件。

        设置为`True`，将转换为`'%Y_%m_%d.log'`格式的文件名。
        '''

        if value is True:
            self._logger = self._app._text.logger
        elif value is False:
            self._logger = ''
        else:
            self._logger = value

        if self.log and self.logger:
            logger.filePath = os.path.join(self.base, self.log, self.logger)
        else:
            logger.filePath = ''
