import blinker

class Signal(dict):
    def register(self, name: str):
        if name in self:
            raise KeyError('The name has been registered')

        self[name] = blinker.signal(name)

    def connect(self, name: str):
        if name not in self:
            raise KeyError('No signal with this name')
        def decorator(func):
            self[name].connect(func, weak = False)
        return decorator

    def receiver(self, name: str):
        if name not in self:
            raise KeyError('No signal with this name')

        return self[name].receivers

    def send(self, name: str, *args, **kwargs):
        if name not in self:
            raise KeyError('No signal with this name')

        self[name].send(*args, **kwargs)

    async def async_send(self, name: str, *args, **kwargs):
        if name not in self:
            raise KeyError('No signal with this name')

        await self[name].send_async(*args, **kwargs)

signal = Signal()

signal.register('server_beforeStartingHandle')
signal.register('worker_beforeStartingHandle')
signal.register('worker_afterStartingHandle')
signal.register('server_afterStartingHandle')
signal.register('context_beforeFirstRequestHandle')
signal.register('http_beforeRequestHandle')
signal.register('http_afterResponseHandle')
signal.register('websocket_beforeConnectionHandle')
signal.register('websocket_afterDisconnectionHandle')
signal.register('worker_beforeStoppingHandle')
signal.register('server_beforeStoppingHandle')
