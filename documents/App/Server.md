# **Server**

该类中有一些与服务器配置相关的信息。

```python
from CheeseAPI import app

app.server
```

## **`app.server.host: IPv4 = '0.0.0.0'`**

在`app.run()`之前设置。暂不支持ipv6。

## **`app.server.port: Port = 5214`**

在`app.run()`之前设置。

## **`app.server.workers: NonNegativeInt = 1`**

在`app.run()`之前设置。设置为`0`的话会自动设置`app.server.workers`为cpu核数 * 2 + 1。

## **`app.server.static: str | None = None`**

服务器静态资源url路径，当`app.server.static is None`时不启用静态资源，反之在`app.workspace.static`中的文件会被映射到`http://0.0.0.0:5214/`，并会优先匹配静态资源。

```python
from CheeseAPI import app

app.server.static = '/'
```

## **`app.server.backlog: int = 128`**

等待处理的请求；建议与QPS相同，过大的参数会拖累性能。
