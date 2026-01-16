# **CheeseAPI**

一款协程友好的 web 框架

该框架为个人设计，仅供学习交流使用，各种 API 目前不会保证稳定性和向后兼容性

## **安装**

```bash
pip install CheeseAPI
```

## **依赖**

1. **[CheeseLog](https://github.com/CheeseUnknown/CheeseLog)**

日志系统，CheeseAPI 使用它进行日志的输出与记录

2. **[CheeseSignal](https://github.com/CheeseUnknown/CheeseSignal)**

信号系统，CheeseAPI 使用它进行所有事件信号的管理与分发

## **项目结构**

CheeseAPI采用模块结构：

```
| - User
    | - __init__.py
    | - model.py
    | - api.py
    | - scheduler.py
    | - service.py
    | - handle.py
    | - validator.py
| - Permission
    | - __init__.py
    | - model.py
    | - api.py
    | - service.py
    | - validator.py
| - __init__.py
| - app.py
```

CheeseAPI 并没有强制规定文件名，但建议的文件命名方式如下：

| 文件名 | 备注 |
| - | - |
| \_\_init\_\_.py | 公用变量 |
| model.py | ORM或类 |
| api.py | API接口 |
| scheduler.py | 定时任务 |
| service.py | 业务逻辑实现 |
| handle.py | 运行逻辑 |
| validator.py | 参数校验 |

## **使用**

创建一个 app 文件 `app.py`：

```python
from CheeseAPI import CheeseAPI, Response

app = CheeseAPI()

@app.route.get('/')
async def index(**kwargs):
    return Response('这里是CheeseAPI！')
```

若在单文件中运行，继续添加入口即可

```python
if __name__ == '__main__':
    app.run()
```

若在多文件项目中运行，可创建一个 `manage.py` 入口文件

```python
from app import app

if __name__ == '__main__':
    app.run()
```

运行入口文件即可

## **示例**

在 `examples` 目录下有一些示例项目，可以参考学习

## **文档**

### 1. [**CheeseAPI（主模块）**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/CheeseAPI.md)

### 2. [**Route（路由）**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/Route.md)

### 3. [**Request**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/Request.md)

### 4. [**Response**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/Response.md)

### 5. [**Websocket**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/Websocket.md)

### 6. [**File**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/File.md)

### 7. [**Validator（数据校验）**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/Validator.md)

### 8. [**Signal**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/Signal.md)

### 9. [**Scheduler（任务调度）**](https://github.com/CheeseUnknown/CheeseAPI/blob/master/documents/Scheduler.md)
