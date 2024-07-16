# **Signal**

CheeseAPI的信号插槽使用[CheeseSignal](https://blinker.readthedocs.io)实现。

所有参数都以`**kwargs`的形式传递。

部分实例参数可在插槽中修改属性，但希望使用自定义的装饰器进行数据的修改，插槽是为了更好的解耦代码而存在。

后续内容会涉及到[Route （路由）](../Route.md)、[Request （请求体）](../Request.md)和[Response （响应体）](../Response.md)，不再阐述。

## **【非协程】 `app.signal.server_beforeStarting: Signal = Signal()`**

server启动前；无法进行web响应。

## **【协程】 `app.signal.server_afterStarting: Signal = Signal()`**

server启动后；此时所有worker都已经启动。

## **【协程】 `app.signal.server_running: Signal = Signal()`**

server运行时可进行逻辑处理，该函数的调用频率为`app.server.intervalTime`，单位为秒。

通常用来处理多worker之间的数据同步问题。

## **【协程】 `app.signal.server_beforeStopping: Signal = Signal()`**

server停止之前；此时所有worker已经停止运行，无法再响应请求。

## **【非协程】 `app.signal.server_afterStopping: Signal = Signal()`**

server停止之后；此插槽执行完后整个程序结束。

## **【非协程】 `app.signal.worker_beforeStarting: Signal = Signal()`**

worker启动前。

## **【协程】 `app.signal.worker_afterStarting: Signal = Signal()`**

worker启动后，此时可以进行请求响应。

## **【协程】 `app.signal.worker_running: Signal = Signal()`**

worker运行时可以进行逻辑处理，该函数的调用频率为`app.server.intervalTime`，单位为秒。

## **【协程】 `app.signal.worker_beforeStopping: Signal = Signal()`**

worker停止前。

## **【非协程】 `app.signal.worker_afterStopping: Signal = Signal()`**

worker停止后。

## **【协程】 `app.signal.http_beforeRequest: Signal = Signal()`**

解析request之前；需要注意的是，websocket请求也触发该插槽。

## **【协程】 `app.signal.http_afterRequest: Signal = Signal()`**

解析request之后。

- **参数**

    - **`request: Request`**

        请求体。

    - **`**kwargs`**

        路由动态参数。

## **【协程】 `app.signal.http_static: Signal = Signal()`**

静态资源插槽；当请求响应的是文件响应体时触发。

- **参数**

    - **`request: Request`**

        请求体。

    - **`response: FileResponse`**

        文件响应体。

    - **`**kwargs`**

        路由动态参数。

## **【协程】 `app.signal.http_custom: Signal = Signal()`**

自定义函数插槽；当请求被路由的自定义函数处理时被调用。

- **参数**

    - **`request: Request`**

        请求体。

    - **`response: BaseResponse`**

        响应体。

    - **`**kwargs`**

        路由动态参数。

## **【协程】 `app.signal.http_404: Signal = Signal()`**

404响应插槽。

- **参数**

    - **`request: Request`**

        请求体。

    - **`response: BaseResponse = Response(http.HTTPStatus.NOT_FOUND)`**

        响应体。

    - **`**kwargs`**

        路由动态参数。

## **【协程】 `app.signal.http_options: Signal = Signal()`**

预请求插槽；该插槽不会响应自定义的OPTIONS响应体。

- **参数**

    - **`request: Request`**

        请求体。

    - **`response: BaseResponse = Response(http.HTTPStatus.OK)`**

        响应体。

    - **`**kwargs`**

        路由动态参数。

## **【协程】 `app.signal.http_405: Signal = Signal()`**

405响应插槽；该插槽不会响应自定义的405响应体。

- **参数**

    - **`request: Request`**

        请求体。

    - **`response: BaseResponse = Response(http.HTTPStatus.METHOD_NOT_ALLOWED)`**

        响应体。

    - **`**kwargs`**

        路由动态参数。

## **【协程】 `app.signal.http_500: Signal = Signal()`**

500响应插槽；该插槽不会响应自定义的500响应体。

- **参数**

    - **`request: Request`**

        请求体。

    - **`response: BaseResponse = Response(http.HTTPStatus.INTERNAL_SERVER_ERROR)`**

        响应体。

    - **`**kwargs`**

        路由动态参数。

## **【协程】 `app.signal.http_beforeResponse: Signal = Signal()`**

Response响应之前。

- **参数**

    - **`request: Request`**

        请求体。

    - **`response: BaseResponse`**

        响应体。

    - **`**kwargs`**

        路由动态参数。

## **【协程】 `app.signal.http_afterResponse: Signal = Signal()`**

Response响应之后；此时response已经发送，对其的任何更改都不再有影响。

- **参数**

    - **`request: Request`**

        请求体。

    - **`response: BaseResponse`**

        响应体。

    - **`**kwargs`**

        路由动态参数。

## **【协程】 `app.signal.websocket_afterRequest: Signal = Signal()`**

Websocket的request解析之后；请注意request解析前会触发`app.signal.http_beforeRequest`插槽，而不是不存在的`app.signal.websocket_beforeRequest`插槽！

- **参数**

    - **`request: Request`**

        请求体。

    - **`**kwargs`**

        路由动态参数。

## **【协程】 `app.signal.websocket_404: Signal = Signal()`**

Websocket 404响应插槽；该插槽在请求升级为websocket后无法匹配对应url时触发。

- **参数**

    - **`request: Request`**

        请求体。

    - **`response: BaseResponse = Response(http.HTTPStatus.NOT_FOUND)`**

        响应体。

    - **`**kwargs`**

        路由动态参数。

## **【协程】 `app.signal.websocket_405: Signal = Signal()`**

Websocket 405响应插槽；该插槽在请求升级为websocket后无法匹配对应method时触发。

- **参数**

    - **`request: Request`**

        请求体。

    - **`response: BaseResponse = Response(http.HTTPStatus.METHOD_NOT_ALLOWED)`**

        响应体。

    - **`**kwargs`**

        路由动态参数。

## **【协程】 `app.signal.websocket_500: Signal = Signal()`**

Websocket 500响应插槽。

- **参数**

    - **`request: Request`**

        请求体。

    - **`response: BaseResponse = Response(http.HTTPStatus.METHOD_NOT_ALLOWED)`**

        响应体。

    - **`**kwargs`**

        路由动态参数。

## **【协程】 `app.signal.websocket_beforeResponse: Signal = Signal()`**

Websocket response响应之前；该插槽仅会在连接失败时触发。

- **参数**

    - **`request: Request`**

        请求体。

    - **`response: BaseResponse = Response(http.HTTPStatus.METHOD_NOT_ALLOWED)`**

        响应体。

    - **`**kwargs`**

        路由动态参数。

## **【协程】 `app.signal.websocket_afterResponse: Signal = Signal()`**

Websocket response响应之后；该插槽仅会在连接失败时触发，此时response已经发送，对其的任何更改都不再有影响。

- **参数**

    - **`request: Request`**

        请求体。

    - **`response: BaseResponse = Response(http.HTTPStatus.METHOD_NOT_ALLOWED)`**

        响应体。

    - **`**kwargs`**

        路由动态参数。

## **【协程】 `app.signal.websocket_beforeSubprotocol: Signal = Signal()`**

Websocket解析子协议之前；该插槽仅会在需要选择子协议的时候触发。

- **参数**

    - **`request: Request`**

        请求体。

    - **`**kwargs`**

        路由动态参数。

## **【协程】 `app.signal.websocket_afterSubprotocol: Signal = Signal()`**

Websocket解析子协议之后；此时仍可以对response进行修改，并尝试建立一个成功的连接。

该插槽执行完毕后，才会正式的连接或断开。

- **参数**

    - **`request: Request`**

        请求体。

    - **`**kwargs`**

        路由动态参数。

## **【协程】 `app.signal.websocket_beforeConnection: Signal = Signal()`**

Websocket连接建立之前；此时已经可以进行消息的发送，该插槽只是`WebsocketServer.connect()`的前置函数。

- **参数**

    - **`request: Request`**

        请求体。

    - **`**kwargs`**

        路由动态参数。

## **【协程】 `app.signal.websocket_afterConnection: Signal = Signal()`**

Websocket连接建立之后。

- **参数**

    - **`request: Request`**

        请求体。

    - **`**kwargs`**

        路由动态参数。

## **【协程】 `app.signal.websocket_beforeMessage: Signal = Signal()`**

Websocket消息获取之前。

- **参数**

    - **`request: Request`**

        请求体。

    - **`message: str | bytes`**

        消息。

    - **`**kwargs`**

        路由动态参数。

## **【协程】 `app.signal.websocket_afterMessage: Signal = Signal()`**

Websocket消息获取之后。

- **参数**

    - **`request: Request`**

        请求体。

    - **`message: str | bytes`**

        消息。

    - **`**kwargs`**

        路由动态参数。

## **【协程】 `app.signal.websocket_beforeSending: Signal = Signal()`**

Websocket发送消息之前。

- **参数**

    - **`request: Request`**

        请求体。

    - **`message: str | bytes`**

        消息。

    - **`**kwargs`**

        路由动态参数。

## **【协程】 `app.signal.websocket_afterSending: Signal = Signal()`**

Websocket发送消息之后。

- **参数**

    - **`request: Request`**

        请求体。

    - **`message: str | bytes`**

        消息。

    - **`**kwargs`**

        路由动态参数。

## **【协程】 `app.signal.websocket_beforeClosing: Signal = Signal()`**

Websocket主动断开连接之前。

- **参数**

    - **`request: Request`**

        请求体。

    - **`code: int`**

        断开代码。

    - **`reason: str | bytes`**

        断开原因。

    - **`**kwargs`**

        路由动态参数。

## **【协程】 `app.signal.websocket_afterClosing: Signal = Signal()`**

Websocket主动断开连接之后。

- **参数**

    - **`request: Request`**

        请求体。

    - **`code: int`**

        断开代码。

    - **`reason: str | bytes`**

        断开原因。

    - **`**kwargs`**

        路由动态参数。

## **【协程】 `app.signal.websocket_afterDisconnection: Signal = Signal()`**

Websocket断开连接之后；注意，`app.signal.websocket_beforeDisconnection`是不存在的。

- **参数**

    - **`request: Request`**

        请求体。

    - **`**kwargs`**

        路由动态参数。

## **【协程】 `app.signal.scheduler_beforeRunning: Signal = Signal()`**

任意任务被执行前；仅有主进程可触发该信号。

- **参数**

    - **`task: SchedulerTask`**

        任务实例。

## **【协程】 `app.signal.scheduler_beforeRunning: Signal = Signal()`**

任意任务被执行后；仅有主进程可触发该信号。

- **参数**

    - **`task: SchedulerTask`**

        任务实例。
