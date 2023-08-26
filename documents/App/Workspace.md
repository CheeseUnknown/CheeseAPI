# **Workspace**

工作空间，该类中有一些与计算机路径相关的内容。

```python
from CheeseAPI import app

app.workspace
```

## **`app.workspace.CheeseAPI: str = os.path.dirname(os.path.realpath(__file__))`**

只读，当前CheeseAPI库的计算机路径。

## **`app.workspace.base: str = os.getcwd()`**

只读，项目的基础路径，目前为当前工作目录。

## **`app.workspace.log: str = './static/'`**

项目静态资源文件夹。如果`app.workspace.log[0] != '.'`，则使用绝对路径进行查找，否则使用基于`app.workspace.base`档相对路径进行查找。

## **`app.workspace.logger: str | None = None`**

当`app.workspace.logger is None`时，CheeseAPI将不生成日志文件。

当设置`app.workspace.logger = True`时，会自动设置`app.workspace.logger = '%Y_%m_%d-%H_%M_%S.log'`

设置`app.workspace.logger`为字符串时，CheeseAPI会尝试将消息写入基于`app.workspace.log`路径的该文件夹。

`app.workspace.log`会被`datatime.datetime`解析，可以使用支持的时间替换符。
