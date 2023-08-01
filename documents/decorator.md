# **装饰器**

## **`@app.server_startingHandle`**

在服务器启动的时候触发，仅触发一次。

## **`@app.server_endingHandle`**

在服务器关闭的时候触发，仅触发一次。若是程序被报错强行中断，则不会触发。

## **`@app.http_response404Handle`**

当`HTTP`返回404状态时触发。自定义返回的404状态不会触发，可选的参数：`request`。

## **`@app.http_response405Handle`**

当`HTTP`返回405状态时触发。自定义返回的405状态不会触发，可选的参数：`request`、动态路由变量。

## **`@app.http_response500Handle`**

当`HTTP`返回500状态时触发。自定义返回的500状态不会触发，可选的参数：`request`、动态路由变量。

## **`@app.http_beforeRequestHandle`**

`HTTP`请求处理之前触发，可选的参数：`request`和动态路由变量。

## **`@app.http_afterResponseHandle`**

`HTTP`响应生成之后触发，可选的参数：`request`、动态路由变量和`response`。在这里你可以做响应返回前的最后一次操作。

## **`@app.websocket_beforeConnectionHandle`**

`WEBSOCKET`连接之前触发，可选的参数：`request`和动态路由变量。

## **`@app.websocket_beforeConnectionHandle`**

`WEBSOCKET`断连之后触发，可选的参数：`request`和动态路由变量。

## **`@app.websocket_errorHandle`**

`WEBSOCKET`处理时抛出异常触发，可选的参数：`request`、动态路由变量和`exception`。

## **`@app.websocket_notFoundHandle`**

`WEBSOCKET`匹配路由错误时触发，可选的参数：`request`。
