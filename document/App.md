# **App**

与其他web框架有所不同的是，CheeseAPI已为用户实例化了`App`，因为底层调用方法可能有所不同。

所有的配置项应当在`app.run()`之前设置完毕，以免出现数据不同步的情况。

```python
from CheeseAPI import app

app.server.host = '0.0.0.0' # 主机地址
app.server.port = 5214 # 端口
app.workspace.logger = True # 根据服务器启动时间自动生成日志文件
app.server.static = '' # 关闭静态资源

app.run()
```

## **`app.server: Server = Server(app)`**

server运行时需要的配置，更多请查看[App - Server](./App/Server.md)。

## **`app.workspace: Workspace = Workspace(app)`**

工作目录相关的配置，都与路径有关，更多请查看[App - Workspace](./App/Workspace.md)。

## **`app.signal: Signal = Signal(app)`**

插槽，更多请查看[App - Signal](./App/Signal.md)。

## **`app.scheduler: Scheduler(app)`**

任务调度，更多请查看[App - Scheduler](./App/Scheduler.md)。

## **`app.managers: Dict[str, Any] = {}`**

多worker间的同步数据：

```python
import multiprocessing

from CheeseAPI import app

manager = multiprocessing.Manager()
app.managers['myLock'] = manager.Lock()

app.run()
```

在任意worker中，都可以读写其value，但无法添加或删除`app.managers`中的key，这是不同步的操作！

```python
from CheeseAPI import app, Response

@app.route.get('/')
async def index(**kwargs):
    with app.manager['lock']:
        return Response('这里是CheeseAPI！')
```

## **`app.g: Dict[str, Any] = { 'startTime': None }`**

在server启动时就固定的数据，不需要在server运行时修改。

```python
from CheeseAPI import app

app.g['my_project_version'] = '1.0.0'

app.run()
```

- **`startTime: None | float = None`**

    在server启动时会自动赋值为`float`类型的时间戳。

## **`app.route: Route = Route()`**

无前缀的路由，更多请查看[Route](./Route.md)。

## **`app.routeBus: RouteBus = RouteBus()`**

路由总线，管理所有的路由，更多请查看[App - RouteBus](./App/RouteBus.md)。

## **`app.cors: Cors = Cors()`**

跨域管理，更多请查看[App - Cors](./App/Cors.md)。

## **`app.modules: List[str] = []`**

加载的插件模块，这部分一般由第三方开发者开发，具体的使用方法最终应参考该模块文档。

请确保该模块是支持CheeseAPI的，并且已经下载至本地仓库：

```
pip install Xxx
```

```python
from CheeseAPI import app

app.modules = [ 'Xxx' ]

app.run()
```

若该插件模块允许分别加载子模块，可如此导入：

```python
from CheeseAPI import app

app.modules = [ 'Xxx.module1', 'Xxx.module2' ]

app.run()
```

最终导入的插件模块都将在启动时的信息中展示。

## **`app.localModules: List[str] = [...]`**

前提：所有本地模块未使用代码导入。

本地模块都是基于`app.workspace.base`路径的文件夹。

默认所有本地模块都会加载，不能确保模块的加载顺序。

若自定义加载的本地模块，可以强制规定加载顺序，并忽略其他未加入的模块：

当前文件结构：

```
| - Module1
    | - ...
| - Module2
    | - ...
| - app.py
```

```python
from CheeseAPI import app

app.localModules = [ 'Module1' ]

app.run()
```

最终导入的本地模块都将在启动时的信息中展示。

## **`app.exclude_localModules: List[str] = []`**

前提：所有本地模块未使用代码导入。

忽略的本地模块；静态文件路径和日志路径会自动忽略，不需要额外添加。

优先级最高，该列表中的模块名若存在于`app.localModules`中，则在加载过程中会忽略该模块。

多用于`app.localModules`为自动导入的时候，可对少数模块进行过滤。

```python
from CheeseAPI import app

app.exclude_localModules = [ 'Module1' ] # 若有Module1模块，则不会加载它

app.run()
```

## **`app.preferred_localModules: List[str] = []`**

前提：所有本地模块未使用代码导入。

优先加载的本地模块，按列表顺序加载。

优先级低于`app.exclude_localModules`，其中的模块名仍优先忽略。

未存在于`app.localModules`的模块仍然不会加载。

```python
from CheeseAPI import app

app.preferred_localModules = [ 'Module1', 'Module2' ] # 若模块名都存在，则先加载Module1，再加载Module2

app.run()
```
