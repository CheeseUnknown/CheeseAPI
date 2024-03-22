# **Workspace**

工作区配置，任何修改都应在`app.run()`之前执行。

```python
import os

from CheeseAPI import app

app.workspace.base = os.getcwd()
app.workspace.static = './static/'
app.workspace.log = './logs/'
app.workspace.logger = True

app.run()
```

## **`app.workspace.base: str = os.getcwd()`**

工作区的基础路径，后续所有操作都将基于该工作区。

## **`app.workspace.static: str = './static/`**

工作区中静态文件的存放路径；若`app.server.static and app.workspace.static`为`False`，则不开启静态资源功能。

## **`app.workspace.log: str = './logs/`**

工作区中日志文件的存放路径；若`app.workspace.log and app.workspace.logger`为`False`，则不输出日志文件。

## **`app.workspace.logger: str = ''`**

当前日志文件名；支持时间模板，会在服务器运行的时候自动转换；若`app.workspace.log and app.workspace.logger`为`False`，则不输出日志文件。

设置为`True`，将转换为`'%Y_%m_%d-%H_%M_%S.log'`格式的文件名。
