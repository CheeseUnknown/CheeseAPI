from typing import Dict

import blinker

class Signal:
    def __init__(self):
        self._values: Dict[str, blinker.NamedSignal] = {}

    def register(self, name: str):
        if name in self._values:
            raise KeyError('this name has been registered')

        self._values[name] = blinker.signal(name)

    def connect(self, name: str):
        if name not in self._values:
            raise KeyError('no signal with this name')

        def decorator(func):
            self._values[name].connect(func, weak = False)
        return decorator

    def receiver(self, name: str):
        if name not in self._values:
            raise KeyError('no signal with this name')
        return self._values[name].receivers

    def send(self, name: str, *args, **kwargs):
        if name not in self._values:
            raise KeyError('no signal with this name')
        self._values[name].send(*args, **kwargs)

    async def send_async(self, name: str, *args, **kwargs):
        if name not in self._values:
            raise KeyError('no signal with this name')
        await self._values[name].send_async(*args, **kwargs)

signal = Signal()

signal.register('server_startingHandle')
signal.register('server_endingHandle')
signal.register('http_response404Handle')
signal.register('http_response405Handle')
signal.register('http_response500Handle')
signal.register('http_beforeRequestHandle')
signal.register('http_afterResponseHandle')
signal.register('websocket_beforeConnectionHandle')
signal.register('websocket_afterDisconnectHandle')
signal.register('websocket_errorHandle')
signal.register('websocket_notFoundHandle')
