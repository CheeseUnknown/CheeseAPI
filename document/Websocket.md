# **Websocket**

## **`class WebsocketServer`**

```python
from CheeseAPI import WebsocketServer, app, Request

@app.route.websocket('/')
class MyWebsocket(WebsocketServer):
    async def subprotocol(self, *, request: Request, **kwargs) -> str | None:
        ...

    async def connection(self, *, request: Request, **kwargs):
        ...

    async def message(self, *, request: Request, message: bytes | str, **kwargs):
        ...

    async def disconnection(self, *, request: Request, **kwargs):
        ...
```

### **`async def subprotocol(self, *, request: Request, **kwargs) -> str | None`**

选择子协议。

### **`async def connection(self, *, request: Request, **kwargs)`**

连接成功后。

### **`async def message(self, *, request: Request, message: bytes | str, **kwargs)`**

接收消息。

### **`async def disconnection(self, *, request: Request, **kwargs)`**

断开连接后。

### **`async def send(self, message: str | bytes)`**

发送消息。

```python
from CheeseAPI import WebsocketServer, app

@app.route.websocket('/')
class MyWebsocket(WebsocketServer):
    async def connection(self, **kwargs):
        await self.send('这里是CheeseAPI！')
```

### **`async def close(self, code: int = 1000, reason: str = '')`**

主动关闭连接。

```python
from CheeseAPI import WebsocketServer, app

@app.route.websocket('/')
class MyWebsocket(WebsocketServer):
    async def message(self, *, message: bytes | str, **kwargs):
        if message == 'over':
            await self.close()
```
