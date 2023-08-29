# **Websocket**

CheeseAPI自带Websocket支持，但仅提供基础功能，如果需要更多扩展功能，请使用[CheeseAPI_Websocket](https://github.com/CheeseUnknown/CheeseAPI_Websocket)。

```python
from CheeseAPI import WebsocketClient, app

@app.route.websocket('/')
class Test(WebsocketClient):
    def subprotocolHandle(self, request: 'Request', subprotocols: List[str], **kwargs) -> str | None:
        ...

    async def connectionHandle(self, request: 'Request', **kwargs):
        ...

    async def messageHandle(self, request: 'Request', message: bytes | str, **kwargs):
        ...

    async def disconnectionHandle(self, request: 'Request', **kwargs):
        ...
```

## **`def subprotocolHandle(self, request: 'Request', subprotocols: List[str], **kwargs) -> str | None`**

当WEBSOCKET请求中携带有protocol时，该函数会被调用，需要对protocol进行解析并返回一个protocol，若返回`None`，则会不进行连接。

- **`**kwargs`**

    其中包含一些多余的参数，例如路由中的变量。

## **`async def connectionHandle(self, request: 'Request', **kwargs)`**

当WEBSOCKET连接成功后调用。

- **`**kwargs`**

    其中包含一些多余的参数，例如路由中的变量。

## **`async def messageHandle(self, request: 'Request', message: bytes | str, **kwargs)`**

接收消息时调用该函数。

- **`**kwargs`**

    其中包含一些多余的参数，例如路由中的变量。

## **`async def disconnectionHandle(self, request: 'Request', **kwargs)`**

当WEBSOCKET连接断开后调用。

- **`**kwargs`**

    其中包含一些多余的参数，例如路由中的变量。

## **`async def send(self, value: str | bytes)`**

发送消息。

```python
from CheeseAPI import WebsocketClient, app

@app.route.websocket('/')
class Test(WebsocketClient):
    async def messageHandle(self, request: 'Request', message: bytes | str, **kwargs):
        self.send(message)
```

## **`async def close(self, code: int = 1000, reason: str = '')`**

主动关闭连接。

```python
from CheeseAPI import WebsocketClient, app

@app.route.websocket('/')
class Test(WebsocketClient):
    async def messageHandle(self, request: 'Request', message: bytes | str, **kwargs):
        if message == 'close':
            self.close()
```
