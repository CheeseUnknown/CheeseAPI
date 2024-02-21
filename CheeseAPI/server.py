import os

class Server:
    def __init__(self) -> None:
        self.host: str = '0.0.0.0'
        self.port: int = 5214
        self._workers: int = 1
        self.static: str | None = None
        self.backlog: int = 128

    @property
    def workers(self) -> int:
        return self._workers

    @workers.setter
    def workers(self, value):
        if value == 0:
            self._workers = os.cpu_count() * 2 + 1
        else:
            self._workers = value
