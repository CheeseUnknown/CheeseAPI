import os, datetime

from CheeseLog import logger

class Workspace:
    def __init__(self):
        self.CheeseAPI: str = os.path.dirname(os.path.realpath(__file__))
        self.base: str = os.getcwd()
        self.static: str = './static/'
        self.log: str = './logs/'
        self._logger: str | bool = False

    @property
    def logger(self) -> str | None:
        return self._logger

    @logger.setter
    def logger(self, value: str | bool):
        from CheeseAPI import app

        if value is True:
            self._logger = datetime.datetime.now().strftime('%Y_%m_%d-%H_%M_%S.log')
        elif value is False:
            logger.filePath = None
            return
        else:
            self._logger = datetime.datetime.now().strftime(str(value))
        logger.filePath = self.log + self._logger

        if 'workspace.logger' in app._managers and app._managers['workspace.logger'].value != logger.filePath:
            app._managers['workspace.logger'].value = self.logger
