import os, datetime

from CheeseLog import logger

class Workspace:
    def __init__(self):
        self.CheeseAPI: str = os.path.dirname(os.path.realpath(__file__))
        self.base: str = os.getcwd()
        self.static: str = './static/'
        self.log: str = './logs/'
        self._logger: str | None = None

    @property
    def logger(self) -> str | None:
        return self._logger

    @logger.setter
    def logger(self, value: str | None):
        if value is True:
            self._logger = datetime.datetime.now().strftime('%Y_%m_%d-%H_%M_%S.log')
        else:
            self._logger = datetime.datetime.now().strftime(str(value))
        logger.filePath = self.base + '/' + self.log + self._logger
