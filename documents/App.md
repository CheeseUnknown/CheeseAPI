# **App**

与其他web框架不同的是，CheeseAPI已经为用户实例化了`App`，因为底层调用方法可能有所不同。

除了一些服务器启动后不会更改的配置，例如host、port、workers之类，其他大部分是可再次配置的。下面列举一些常用的配置项：

```python
from CheeseAPI import app

app.server.port = 8000 # 修改端口号
app.server.workers = 0 # 修改worker数量为自动
app.workspace.logger = True # 自动生成日志文件
app.server.static = '/' # 启用静态资源，访问地址为GET /

if __name__ == '__main__':
    app.run()
```

## **`app.workspace: Workspace`**

工作目录，更多请查看[App - Workerspace](./App/Workspace.md)。

## **`app.server: Server`**

服务器相关，更多请查看[App - Server](./App/Server.md)。

## **`app.route: Route`**

基础路由，更多请查看[Route](./Route.md)。

## **`app.cors: Cors`**

跨域设置，更多请查看[Cors](./App/Cors.md)。

## **`app.modules: List[str] = []`**

模块。如果在python库中适配于CheeseAPI的库，可以添加库名以导入到项目中，下面以[CheeseAPI_Websocket](https://github.com/CheeseUnknown/CheeseAPI_Websocket)为例：

```bash
pip install CheeseAPI_Websocket
```

```python
from CheeseAPI import app

app.modules = [ 'CheeseAPI_Websocket' ]
```

如果你是插件开发者，更多模块开发内容请查看[Module](./Module.md)。

## **`app.localModules: List[str] | Literal[True] = True`**

本地模块。当`app.localModules == True`时，在当前工作目录下，会自动导入文件夹中第一层的python文件（忽略隐藏文件夹、`__pycache__`、`__init__.py`以及一些`app.workspace`中使用的文件夹）；如果需要选择性的导入本地模块，请赋值`List[str]`，会遵循列表顺序依次加载模块：

```python
from CheeseAPI import app

app.localModules = [ 'testModule0', 'testModule1' ]
```

## **`app.exclude_localModules: List[str] = []`**

当`app.localModules is True`时，可以选择不导入的模块，而不需要手动添加需要的模块。

```python
from CheeseAPI import app

app.exclude_localModules = [ 'testModule0', 'testModule1' ]
```

## **`app.preferred_localModules: List[str] = []`**

当`app.localModules is True`时，可以选择优先导入的模块，按列表顺序依次加载。

```python
from CheeseAPI import app

app.preferred_localModules = [ 'firstModule', 'secondModule' ]
```

## **`app.handle: Handle`**

插槽，更多请查看[App - Handle](./App/Handle.md)。

## **`app.g: Dict[str, Any] = {}`**

全局变量，你可以设置一些全局需要的额外参数。

## **`def app.run()`**

启动服务器。

## **`def app.stop()`**

关闭服务器
