# **CheeseAPI**

## **介绍**

一款协程友好的web框架，它具有以下功能：

1. 插件支持，更可塑的事件处理以及个性化设置。

2. 以模块为主的项目结构，以及灵活的模块导入方式。

3. Websocket支持。

暂时未添加的功能：

1. ssl证书。

2. http2协议支持。

3. 部分不常用请求的处理方式可能有误。

目前项目仍处于开发状态，有大部分功能尚不稳定或未提供，对于一些功能未来不能确保支持。

## **安装**

系统要求：Linux。

Python要求：目前仅保证支持3.11及以上版本的Python，新版本会优先支持Python的最新稳定版本。

```
pip install CheeseAPI
```

## **依赖**

1. **[CheeseLog](https://github.com/CheeseUnknown/CheeseLog)**

日志系统，CheeseAPI使用它进行日志的输出与记录。

## **项目结构**

CheeseAPI采用模块结构：

```
| - User
    | - __init__.py
    | - model.py
    | - api.py
    | - service.py
    | - handle.py
| - Permission
    | - __init__.py
    | - model.py
    | - api.py
    | - service.py
| - __init__.py
| - app.py
```

CheeseAPI并没有强制规定文件名，但建议的文件命名方式如下：

| 文件名 | 备注 |
| - | - |
| \_\_init\_\_.py | 公用变量 |
| model.py | ORM或类 |
| api.py | API接口 |
| service.py | 业务逻辑实现 |
| handle.py | 插槽逻辑 |

一般来说，模块中的文件调用有明显的顺序关系（从顶层到底层）：

```
handle.py ---
            |-> service.py -> model.py -> __init__.py
api.py ------
```

## **使用**

创建一个启动入口文件`app.py`：

```python
from CheeseAPI import app, Response

@app.route.get('/')
async def index(**kwargs):
    return Response('这里是CheeseAPI！')

app.run()
```

运行`app.py`，可以看到打印了一些服务器的基本信息：

```
$ python app.py
(STARTING) 2024-03-19 14:03:12.405969 > The master process 346 started
(STARTING) 2024-03-19 14:03:12.406156 > Workspace Information:
    Base: /home/cheese/Code/CheeseAPI
    Static: ./static/
(STARTING) 2024-03-19 14:03:12.406235 > Server Information:
    Host: 0.0.0.0
    Port: 5214
    Workers: 1
    Backlog: 1024
    Static: /
(LOADED) 2024-03-19 14:03:12.418829 > Local Modules:
    CheeseAPI
(DEBUG) 2024-03-19 14:03:12.418939 > The process 346 started
(STARTING) 2024-03-19 14:03:12.419363 > The server started on 0.0.0.0:5214
```

出现`The process xxx started`日志时，代表其中某个worker已启动，此时已经可以进行网络请求访问；出现`The server started on 0.0.0.0:5214`日志时，代表服务器已完全启动。

使用`ctrl + c`或`kill`命令杀死主进程，会输出结束日志，此时整个程序才算正式关闭：

```
(DEBUG) 2024-03-19 14:05:40.350681 > The process 346 stopped
(ENDING) 2024-03-19 14:05:40.350816 > The server runs for a total of 2 minutes 27.944854 seconds
(ENDING) 2024-03-19 14:05:40.350849 > The master process 346 stopped
```

## **更多...**

### 1. [**App （主模块）**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/document/App.md)

#### 1.1 [**Server （服务器配置）**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/document/App/Server.md)

#### 1.2 [**Workspace （工作区配置）**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/document/App/Workspace.md)

#### 1.3 [**Signal （信号插槽）**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/document/App/Signal.md)

#### 1.4 [**RouteBus （路由总线）**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/document/App/RouteBus.md)

#### 1.5 [**Cors （跨域管理）**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/document/App/Cors.md)

### 2. [**Request （请求体）**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/document/Request.md)

### 3. [**Response （响应体）**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/document/Response.md)

### 4. [**Route （路由）**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/document/Route.md)

### 5. [**Websocket**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/document/Websocket.md)

### 6. [**File （文件）**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/document/File.md)

### 7. [**For 开发者**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/document/Developer.md)

## **可用的插件模块**

### 1. **[CheeseAPI_Websocket](https://github.com/CheeseUnknown/CheeseAPI_Websocket)**

websocket的升级插件，支持了更多、更便捷的通讯方式。
