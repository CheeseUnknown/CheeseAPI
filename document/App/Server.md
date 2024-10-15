# **Server**

服务器配置，任何修改都应在`app.run()`之前执行

```python
from CheeseAPI import app

app.server.host = '0.0.0.0'
app.server.port = 5214
app.server.workers = 1

app.run()
```

## **`app.server.host: str = '0.0.0.0'`**

服务器主机ip地址，支持ipv6

## **`app.server.port: int = 5214`**

服务器端口

## **`app.server.workers: int = 1`**

worker数量；若设置为0，则自动设置为cpu数量*2+1

## **`app.server.backlog: int = 1024`**

排队连接的最大数量

## **`app.server.static: str = '/`**

静态资源在路由中的路径；若`app.server.static and app.workspace.static`为`False`，则不开启静态资源功能

访问`GET /file`会进行以下判断，若匹配成功则不继续匹配（以默认的static工作区为基础路径）：

1. 查找文件`./static/file`

2. 查找文件`./static/file.html`

3. 查找文件`./static/file/index.html`

4. 查找`GET /file`的自定义响应

若访问路由最后一位为`/`，这意味着访问一个文件夹，返回一个404的响应是正常的，因为CheeseAPI并不提供静态资源的路由功能

## **`app.server.intervalTime: float = 0.016`**

服务器处理间隔时间，单位为秒；越小的处理间隔意味着服务器对于某些特定的响应会更快
