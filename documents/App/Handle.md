# **Handle**

具体的调用顺序请查看[生命周期](../生命周期.md)。

所有的插槽都在此处，如果你是普通的开发用户，不需要了解这部分。

```python
import os

from CheeseAPI import app
from CheeseAPI.handle import Handle

# 直接赋值以替换最新的插槽
def _worker_beforeStartingHandle():
    print(f'The subprocess {os.getpid()} started')
app.handle._worker_beforeStartingHandle = _worker_beforeStartingHandle

# 继承Handle类
class MyHandle(Handle):
    def _worker_beforeStartingHandle(self):
        print('Hellow World')
        super()._worker_beforeStartingHandle()
app.handle = MyHandle()
```

## **`app.handle._server_beforeStartingHandle()`**

服务器启动前事件插槽。

## **`app.handle._worker_beforeStartingHandle()`**

worker启动前事件插槽。

## **`app.handle._server_afterStartingHandle()`**

服务器启动后事件插槽。

## **`app.handle._httpHandle(protocol: HttpProtocol, app: App)`**

HTTP总处理事件插槽。

## **`app.handle._http_staticHandle(protocol: HttpProtocol, app: App)`**

HTTP静态资源处理事件插槽。

## **`app.handle._http_404Handle(protocol: HttpProtocol, app: App)`**

HTTP 404处理事件插槽。

## **`app.handle._http_optionsHandle(protocol: HttpProtocol, app: App)`**

HTTP OPTIONS预请求处理事件插槽。

## **`app.handle._http_405Handle(protocol: HttpProtocol, app: App)`**

HTTP 405处理事件插槽。

## **`app.handle._http_noResponseHandle(protocol: HttpProtocol, app: App)`**

HTTP 自定义函数没有返回[Response](../Response.md)。

## **`app.handle._http_500Handle(protocol: HttpProtocol, app: App, e: BaseException)`**

HTTP 500处理事件插槽。

## **`app.handle._http_responseHandle(protocol: HttpProtocol, app: App, response: 'Response', timer: float)`**

HTTP 返回[Response](../Response.md)处理事件插槽。

## **`app.handle._websocket_requestHandle(self, protocol: WebsocketProtocol, app: App) -> Tuple[Callable, Dict[str, Any]] | HTTPResponse`**

WEBSOCKET [Request](../Request.md)响应处理事件插槽。

## **`app.handle._websocket_404Handle(protocol: WebsocketProtocol, app: App) -> Response`**

WEBSOCKET 404处理事件插槽。

## **`app.handle._websocket_405Handle(protocol: WebsocketProtocol, app: App) -> Response`**

WEBSOCKET 405处理事件插槽。

## **`app.handle._websocket_responseHandle(protocol: WebsocketProtocol, app: App) -> HTTPResponse`**

WEBSOCKET [Response](../Response.md)处理事件插槽。

## **`app.handle._websocket_subprotocolHandle(protocol: WebsocketProtocol, app: App) -> str | None:`**

WEBSOCKET subprotol处理事件插槽。

## **`app.handle._websocket_connectionHandle(protocol: WebsocketProtocol, app: App)`**

WEBSOCKET连接事件插槽。

## **`app.handle._websocket_messageHandle(protocol: WebsocketProtocol, app: App)`**

WEBSOCKET消息接收事件插槽。

## **`app.handle._websocket_disconnectionHandle(protocol: WebsocketProtocol, app: App)`**

WEBSOCKET断开连接事件插槽。

## **`app.handle._worker_beforeStoppingHandle()`**

worker停止前事件插槽

## **`app.handle._server_beforeStoppingHandle()`**

服务器停止前事件插槽。
