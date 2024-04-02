import os, sys

from typing import TYPE_CHECKING

from CheeseLog import logger

if TYPE_CHECKING:
    from CheeseAPI.app import App

class Workspace:
    def __init__(self, app: 'App'):
        self._app: 'App' = app

        self._base: str = os.getcwd()
        self.static: str = './static/'
        self._log: str = './logs/'
        self._logger: str = ''

    @property
    def base(self) -> str:
        return self._base

    @base.setter
    def base(self, value: str):
        try:
            sys.path.remove(self._base)
        except:
            ...
        self._base = value
        sys.path.append(self._base)

    @property
    def log(self) -> str:
        return self._log

    @log.setter
    def log(self, value: str):
        self._log = value

        if self.log and self.logger:
            logger.filePath = os.path.join(self.log, self.logger)
        else:
            logger.filePath = ''

    @property
    def logger(self) -> str:
        return self._logger

    @logger.setter
    def logger(self, value: str | bool):
        if value is True:
            self._logger = self._app._text.logger
        elif value is False:
            self._logger = ''
        else:
            self._logger = value

        if self.log and self.logger:
            logger.filePath = os.path.join(self.log, self.logger)
        else:
            logger.filePath = ''
