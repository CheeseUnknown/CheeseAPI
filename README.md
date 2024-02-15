# **CheeseAPI**

## **介绍**

一款协程友好的web框架，它有大部分框架都有的功能，以及它的特点：

1. 插件支持，更可塑的事件处理。

2. 类Django的项目结构。

3. Websocket支持。

目前项目仍处于开发阶段，有大部分功能尚未提供，文档极不稳定，对于一些功能未来不确保能一直支持。

## **安装**

系统要求：Linux。

Python要求：目前仅保证支持3.11及以上的python。

```bash
pip install CheeseAPI
```

## **使用**

### **简单的示例**

目前只支持在当前工作目录下运行。

创建一个启动入口：

```python
# File path: ./app.py

from CheeseAPI import app, Response

@app.route.get('/')
async def test(**kwargs):
    return Response('您好，这里是CheeseAPI！')

app.run() # 默认的启动地址：0.0.0.0，默认的启动端口：5214
```

运行`app.py`，可以看到打印了一些基础信息，当当前代码的最后一行启动时，代表系统已经可以访问：

```bash
$ python app.py
(STARTING) 2023-08-24 12:20:56.933161 > The master process 700506 started
(STARTING) 2023-08-24 12:20:56.934117 > Workspace information:
    CheeseAPI: /xxx/CheeseAPI/CheeseAPI
    Base: /xxx/CheeseAPI
(STARTING) 2023-08-24 12:20:56.934274 > Server information:
    Host: 0.0.0.0
    Port: 5214
    Workers: 1
(LOADED) 2023-08-24 12:20:56.934619 > Local Modules:
    CheeseAPI
(DEBUG) 2023-08-24 12:20:56.938326 > The subprocess 700506 started
(STARTING) 2023-08-24 12:20:56.939158 > The server started on http://0.0.0.0:5214
```

使用`ctrl + c`或`kill <pid>`杀死进程，会打印完剩下的内容：

```bash
(DEBUG) 2023-08-24 12:29:19.061431 > The 701056 subprocess stopped
(ENDING) 2023-08-24 12:29:19.062018 > The server runs for a total of 11.326843 seconds
(ENDING) 2023-08-24 12:29:19.062144 > The master process 701056 stopped
```

## **项目结构**

CheeseAPI采用类Django的结构：

```
| - User
    | - model.py
    | - api.py
    | - service.py
| - Permission
    | - model.py
    | - api.py
    | - service.py
| - app.py
```

在项目根目录下的文件夹（不包括隐藏文件夹）内的文件会在项目启动时自动导入。

在CheeseAPI中并没有强制规定文件名与其代码的关联性，但建议的文件命名方式如下：

| 文件名 | 备注 |
| - | - |
| model.py | 模型类 |
| api.py | api接口 |
| service.py | 业务逻辑实现 |
| model.py | ORM |
| handle.py | 初始化逻辑 |

## **更多...**

### 1. [**App**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/App.md)

#### 1.1 [**Workspace**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/App/Workspace.md)

#### 1.2 [**Server**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/App/Server.md)

#### 1.3 [**Cors**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/App/Cors.md)

### 2. [**Route**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/Route.md)

### 3. [**Request**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/Request.md)

### 4. [**Response**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/Response.md)

### 5. [**Websocket**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/Websocket.md)

### 6. [**Module**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/Module.md)

### 7. [**Signal**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/Signal.md)

### 8. [**File**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/File.md)
