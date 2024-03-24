# **For 开发者**

此页文档是为更底层的开发者所编写的，部分类型可能未在文档上展示，请以源代码为准。

## **自定义日志内容显示**

CheeseAPI采用[CheeseLog](https://github.com/CheeseUnknown/CheeseLog)进行日志输出，部分模版内容可遵循CheeseLog设置。

对具体内容进行自定义配置，可通过`app._text`进行设置或替换对应函数。

部分默认值由于过长，不予显示，请查看源代码。

### **`app._text.response_server: str = 'CheeseAPI'`**

Response请求headers中的Server项。

### **`app._text.process_title: str = 'CheeseAPI'`**

程序主进程的进程名。

### **`app._text.workerProcess_title: str = 'CheeseAPI:Process'`**

程序子进程的进程名。

### **`app._text.logger: str = '%Y_%m_%d-%H_%M_%S.log'`**

`app.workspace.logger`为`True`时自动设置的值。

### **`app._text.server_information() -> List[Tuple[str, str]]`**

Server的基础信息。

- **返回**

    List的item数代表logger的日志条数；Tuple的两位代表无样式日志与样式日志。（后续不再重复）

### **`app._text.loadingModule(precent: float, module: str) -> Tuple[str, str]`**

正在加载的插件模块信息。

- **参数**

    - **precent**

        加载的百分比进度，范围为[0, 1]。

    - **module**

        插件模块名。

### **`app._text.loadedModules() -> List[Tuple[str, str]]`**

加载完毕后的插件模块信息总览。

### **`app._text.loadingLocalModule(precent: float, module: str) -> Tuple[str, str]`**

正在加载的本地模块信息。

- **参数**

    - **precent**

        加载的百分比进度，范围为[0, 1]。

    - **module**

        本地模块名。

### **`app._text.loadedLocalModules() -> List[Tuple[str, str]]`**

加载完毕后的本地模块信息总览。

### **`app._text.worker_starting() -> List[Tuple[str, str]]`**

Worker启动的信息。

### **`app._text.server_starting() -> List[Tuple[str, str]]`**

Server启动的信息。

### **`app._text.http(protocol: HttpProtocol) -> List[Tuple[str, str]]`**

Http请求访问的信息。

### **`app._text.http_500(protocol: HttpProtocol, e: BaseException) -> List[Tuple[str, str]]`**

Http请求中出现非自定义500错误时的信息。

### **`app._text.websocket_response(protocol: WebsocketProtocol) -> List[Tuple[str, str]]`**

Websocket连接失败，返回的response信息。

### **`app._text.websocket_500(protocol: WebsocketProtocol, e: BaseException) -> List[Tuple[str, str]]`**

Websocket连接出现报错，返回的500 response信息。

### **`app._text.websocket_connection(protocol: WebsocketProtocol) -> List[Tuple[str, str]]`**

Websocket连接成功的信息。

### **`app._text.websocket_disconnection(protocol: WebsocketProtocol) -> List[Tuple[str, str]]`**

Websocket断开连接的信息。

### **`app._text.worker_stopping() -> List[Tuple[str, str]]`**

Worker停止的信息。

### **`app._text.server_stopping() -> List[Tuple[str, str]]`**

Server停止的信息。

## **更底层的插槽**

在`app._handle`中，所有插槽都是整个程序的实现逻辑，除非需要对底层功能进行修改，否则请不要随意修改。

具体内容请查看源代码，修改后请测试基础功能是否完善。

## **编写插件模块**

插件模块分为单模块插件和多模块插件，它们的结构大致是：

```
# 单模块
| - __init__.py
| - file1.py
| - file2.py

# 多模块
| - __init__.py
| - module1
    | - file1.py
    | - file2.py
| - module2
    | - file3.py
```

所有CheeseAPI需要的配置项需存在顶层的__init__.py中。

### **单模块**

单模块可以忽略以下配置，CheeseAPI会提供忽略项。

```python
# /__init__.py

CheeseAPI_module_type = 'single'
```

- ****

### **多模块**

```python
# /__init__.py

CheeseAPI_module_type = 'multiple'
```

### **公用属性**

- **`CheeseAPI_module_dependencies: List[str] = []`**

    可选的。

    所依赖的插件模块，会在加载该模块前先行加载依赖模块。

- **`CheeseAPI_module_preferredSubModules: List[str] = []`**

    可选的。

    对当前模块的某些子模块进行优先加载。
