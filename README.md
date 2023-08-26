# **CheeseAPI**

## **介绍**

一款协程友好的web框架，它有大部分框架都有的功能，以及它的特点：

1. 插件支持，更可塑的事件处理。

2. 类Django的项目结构。

3. Websocket支持。

4. 支持部分配置项动态设置。

目前项目仍处于开发阶段，未来期望提供的功能：

1. 对于请求更完善的处理。

2. 更好的架构设计以及更快的算法处理。

3. 更多的插件。

4. 提供命令，以方便管理项目。

5. 自定义的工作目录。

6. 更多的配置选项。

## **安装**

目前仅支持linux python3.11，这里也推荐将python升级到3.11。

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

'''
路由装饰器装饰的函数参数是可选的，如果你需要获取request，则：
async def test(request):
    ...
即可，其他参数都是动态获取的。
'''
@app.route.get('/')
async def test():
    return Response('您好，这里是CheeseAPI！')

if __name__ == '__main__':
    app.run() # 默认的启动地址：'0.0.0.0'，默认的启动端口：5214
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
(STARTING) 2023-08-24 12:20:56.934619 > Local Modules:
    CheeseAPI
(LOADED) 2023-08-24 12:20:56.937603 > The local modules are loaded, which takes 0.002867 seconds
(DEBUG) 2023-08-24 12:20:56.938326 > The subprocess 700506 started
(STARTING) 2023-08-24 12:20:56.939158 > The server started on http://0.0.0.0:5214
(STARTING) 2023-08-24 12:20:56.939279 > The server startup takes 0.006139 seconds
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

## **更多...**

### 1. [**生命周期**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/生命周期.md)

### 2. [**App**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/App.md)

#### 2.1 [**Workspace**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/App/Workspace.md)

#### 2.2 [**Server**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/App/Server.md)

#### 2.3 [**Cors**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/App/Cors.md)

#### 2.4 [**Handle**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/App/Handle.md)

### 3. [**Route**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/Route.md)

### 4. [**Request**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/Request.md)

### 5. [**Response**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/Response.md)

### 6. [**Websocket**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/Websocket.md)

### 7. [**Module**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/Module.md)

### 8. [**Signal**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/Signal.md)
