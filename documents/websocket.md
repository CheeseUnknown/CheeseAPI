# **websocket**

注意，不要在装饰器函数内直接使用循环，请使用协程调用，以免无法结束该连接。

```python
import asyncio

from CheeseAPI import websocket

@app.route('/', [ 'WEBSOCKET' ])
async def a(request, type, value):
    async def b():
        while websocket.isOnline:
            await websocket.send(value)
            await asyncio.sleep(1)
    asyncio.create_task(b())
```

传入参数有一些规则：

| 参数 | 注释 |
| - | - |
| type | 连接成功返回`'connect'`，接收消息返回`'receive'`，连接断开返回`'disconnect'` |
| value | 当接收消息时，该参数为消息内容，其他事件则返回`None` |

如果你想在连接的时候直接断开连接，可以抛出一个`WebsocketDisconnect`的异常：

```python
from CheeseAPI import websocket, WebsocketDisconnect

@app.route('/', [ 'WEBSOCKET' ])
async def a(type, value):
    if type == 'connect':
        raise WebsocketDisconnect()
```

## **`websocket`**

```python
from CheeseAPI import websocket
```

### **`async websocket.send(message: any, path: str, sid: str | list[str] | None = None)`**

`sid`为`None`，向所有在线用户广播消息。

`sid`为`list[str]`，向所选用户广播消息。

`sid`为`str`，向指定用户发送消息。

### **`async websocket.close(path: str, sid: str | list[str] | None = None)`**

主动关闭连接。`sid`与`send()`功能相同。
