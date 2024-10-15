# **Websocket**

## **`class WebsocketServer`**

```python
from CheeseAPI import WebsocketServer, app, Request

@app.route.websocket('/')
class MyWebsocket(WebsocketServer):
    def __init__(self):
        ''' 两种方法设置Websocket的属性，其中展示的属性是默认值，实际情况根据需求添加即可，不需要修改全部 '''
        # 通过另外设置修改Websocket属性
        super().__init__()
        self.open_timeout: float | None = 10
        self.ping_interval: float | None = 20
        self.ping_timeout: float | None = 20
        self.close_timeout: float | None = None
        self.max_size: int | None = 2**20
        self.max_queue: int | None = 2**5
        self.read_limit: int = 2**16
        self.write_limit: int = 2**16

        # 通过继承方法修改Websocket属性
        super().__init__(open_timeout = 10, ping_interval = 20, ping_timeout = 20, close_timeout = None, max_size = 2**20, max_queue = 2**5, read_limit = 2**16, write_limit = 2**16)

    async def subprotocol(self, *, request: Request, **kwargs) -> str | None:
        ...

    async def connection(self, *, request: Request, **kwargs):
        ...

    async def message(self, *, request: Request, message: bytes | str, **kwargs):
        ...

    async def disconnection(self, *, request: Request, **kwargs):
        ...
```

### **`self.open_timeout: float | None`**

建立连接的超时时间

### **`self.ping_interval: float | None`**

ping间隔时间

### **`self.ping_timeout: float | None`**

ping的超时时间

### **`self.close_timeout: float | None`**

关闭连接的超时时间

### **`self.max_size: int | None`**

消息的最大长度限制

### **`self.max_queue: int | None`**

消息的最大等待个数

### **`self.read_limit: int`**

每次读取的长度限制

### **`self.write_limit: int`**

每次发送的长度限制

### **`async def subprotocol(self, *, request: Request, **kwargs) -> str | None`**

选择子协议

### **`async def connection(self, *, request: Request, **kwargs)`**

连接成功后

### **`async def message(self, *, request: Request, message: bytes | str, **kwargs)`**

接收消息

### **`async def disconnection(self, *, request: Request, **kwargs)`**

断开连接后

### **`async def send(self, message: str | bytes)`**

发送消息

```python
from CheeseAPI import WebsocketServer, app

@app.route.websocket('/')
class MyWebsocket(WebsocketServer):
    async def connection(self, **kwargs):
        await self.send('这里是CheeseAPI！')
```

### **`async def close(self, code: int = 1000, reason: str = '')`**

主动关闭连接

```python
from CheeseAPI import WebsocketServer, app

@app.route.websocket('/')
class MyWebsocket(WebsocketServer):
    async def message(self, *, message: bytes | str, **kwargs):
        if message == 'over':
            await self.close()
```
