import os, socket
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from CheeseAPI.app import App

class Server:
    def __init__(self, app: 'App'):
        self._app: 'App' = app

        self.host: str = '0.0.0.0'
        self.port: int = 5214
        self._workers: int = 1
        self.backlog: int = 1024
        self.static: str = '/'
        self.intervalTime: float = 0.016

    @property
    def workers(self) -> int:
        return self._workers

    @workers.setter
    def workers(self, value: int):
        if value == 0:
            self._workers = os.cpu_count() * 2 + 1
        else:
            self._workers = value
