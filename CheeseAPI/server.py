import os, datetime

import CheeseType, CheeseType.network

class Server:
    def __init__(self, app):
        from .app import App

        self._app: App = app
        self.HOST: CheeseType.network.IPv4 = '127.0.0.1'
        self.PORT: CheeseType.network.Port = 5214
        self._WORKERS: CheeseType.NonNegativeInt = 1
        self.IS_RELOAD: bool = False

        self._IS_DEBUG: bool = False
        self._IS_REQUEST_LOGGED: bool = True

        self._STATIC_PATH: bool | str = False
        self._LOG_FILENAME: bool | str = False

    @property
    def WORKERS(self) -> CheeseType.NonNegativeInt:
        return self._WORKERS

    @WORKERS.setter
    def WORKERS(self, value):
        value = CheeseType.NonNegativeInt(value)
        if value == 0:
            self._WORKERS = os.cpu_count() * 2
        else:
            self._WORKERS = value

    @property
    def IS_DEBUG(self) -> bool:
        return self._IS_DEBUG

    @IS_DEBUG.setter
    def IS_DEBUG(self, value):
        self._IS_DEBUG = CheeseType.Bool(value)
        if isinstance(self._app.logger.filter, set):
            if not self._IS_DEBUG:
                self._app.logger.filter.add('DEBUG')
            elif self._IS_DEBUG:
                if 'DEBUG' in self._app.logger.filter:
                    self._app.logger.filter.remove('DEBUG')

    @property
    def IS_REQUEST_LOGGED(self) -> bool:
        return self._IS_REQUEST_LOGGED

    @IS_REQUEST_LOGGED.setter
    def IS_REQUEST_LOGGED(self, value):
        self._IS_REQUEST_LOGGED = CheeseType.Bool(value)
        if isinstance(self._app.logger.filter, set):
            if not self._IS_REQUEST_LOGGED:
                self._app.logger.filter.add('HTTP')
                self._app.logger.filter.add('WEBSOCKET')
            elif self._IS_REQUEST_LOGGED:
                if 'HTTP' in self._app.logger.filter:
                    self._app.logger.filter.remove('HTTP')
                if 'WEBSOCKET' in self._app.logger.filter:
                    self._app.logger.filter.remove('WEBSOCKET')

    @property
    def LOG_FILENAME(self) -> str | bool:
        return self._LOG_FILENAME

    @LOG_FILENAME.setter
    def LOG_FILENAME(self, value):
        if self._app.process.name == 'MainProcess':
            if value is not False:
                if value is True:
                    self._LOG_FILENAME = datetime.datetime.now().strftime('%Y_%m_%d-%H_%M_%S.log')
                else:
                    self._LOG_FILENAME = datetime.datetime.now().strftime(str(value))
                self._app.logger.filePath = os.path.join(self._app.workspace.BASE_PATH + self._app.workspace.LOG_PATH + self.LOG_FILENAME)
            elif value is False:
                self._LOG_FILENAME = False
                self._app.logger.filePath = None
        else:
            logPath = os.path.join(self._app.workspace.BASE_PATH + self._app.workspace.LOG_PATH)
            logFiles = [ os.path.join(logPath, file) for file in os.listdir(logPath) if os.path.isfile(os.path.join(logPath, file)) ]
            if not logFiles:
                self._LOG_FILENAME = False
                self._app.logger.filePath = None
            else:
                logFile = max(logFiles, key = os.path.getmtime)
                self._LOG_FILENAME = logFile.split('/')[-1]
                self._app.logger.filePath = logFile

    @property
    def STATIC_PATH(self) -> str | bool:
        return self._STATIC_PATH

    @STATIC_PATH.setter
    def STATIC_PATH(self, value):
        if value is not False:
            if value is True:
                self._STATIC_PATH = '/'
            else:
                self._STATIC_PATH = str(value)
        elif value is False:
            self._STATIC_PATH = False
