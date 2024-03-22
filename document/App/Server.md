# **Server**

服务器配置，任何修改都应在`app.run()`之前执行。

```python
from CheeseAPI import app

app.server.host = '0.0.0.0'
app.server.port = 5214
app.server.workers = 1

app.run()
```

## **`app.server.host: str = '0.0.0.0'`**

服务器主机ip地址，支持ipv6。

## **`app.server.port: int = 5214`**

服务器端口。

## **`app.server.workers: int = 1`**

worker数量；若设置为0，则自动设置为cpu数量*2+1。

## **`app.server.backlog: int = 1024`**

排队连接的最大数量。

## **`app.server.static: str = '/`**

静态资源在路由中的路径；若`app.server.static and app.workspace.static`为`False`，则不开启静态资源功能。

## **`app.server.intervalTime: float = 0.016`**

服务器处理间隔时间，单位为秒；越小的处理间隔意味着服务器对于某些特定的响应会更快。
