import os

from CheeseType import IPv4, Port, NonNegativeInt

class Server:
    def __init__(self) -> None:
        self.host: IPv4 = '0.0.0.0'
        self.port: Port = 5214
        self._workers: NonNegativeInt = 1
        self.static: str | None = None

    @property
    def workers(self) -> NonNegativeInt:
        return self._workers

    @workers.setter
    def workers(self, value):
        value = NonNegativeInt(value)
        if value == 0:
            self._workers = os.cpu_count() * 2 + 1
        else:
            self._workers = value
