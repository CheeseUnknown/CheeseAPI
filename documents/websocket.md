# **websocket**

注意，不要在装饰器函数内直接使用循环，请使用协程调用，以免无法结束该连接。

```python
import asyncio

from CheeseAPI import websocket

@app.route('/', [ 'WEBSOCKET' ])
async def a(request, value):
    async def b():
        while websocket.isOnline:
            await websocket.send(value)
            await asyncio.sleep(1)
    asyncio.create_task(b())
```

## **`class Websocket`**

### **`async def send(self, message: any, path: str, sid: str | list[str] | None = None)`**

`sid`为`None`，向所有在线用户广播消息。

`sid`为`list[str]`，向所选用户广播消息。

`sid`为`str`，向指定用户发送消息。

### **`async def close(self, sid: str)`**

主动关闭某个`sid`的连接。

### **`def isOnline(self, sid: str) -> bool`**

判断某个`sid`是否在线。
