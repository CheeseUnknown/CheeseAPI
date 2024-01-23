# **Workspace**

工作空间，该类中有一些与计算机路径相关的内容。

```python
from CheeseAPI import app

app.workspace
```

## **`app.workspace.CheeseAPI: str = os.path.dirname(os.path.realpath(__file__))`**

当前CheeseAPI库的计算机路径。

## **`app.workspace.base: str = os.getcwd()`**

项目的基础路径。

## **`app.workspace.static: str = './static/'`**

项目静态资源文件夹。

## **`app.log: str = './logs/`**

日志文件的基础目录。

## **`app.workspace.logger: str | bool = False`**

当`app.workspace.logger is False`时，CheeseAPI将不生成日志文件。

当设置`app.workspace.logger is True`时，会自动设置`app.workspace.logger = '%Y_%m_%d-%H_%M_%S.log'`

设置`app.workspace.logger`为字符串时，CheeseAPI会尝试将消息写入基于`app.workspace.log`路径的该文件夹。

`app.workspace.log`会被`datatime.datetime`解析，可以使用支持的时间替换符。
