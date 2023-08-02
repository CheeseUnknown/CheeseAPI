# **CheeseAPI**

请注意，该文档是最新的beta版，如果你想要查看最新的发布版内容，请查看最新的tag。

## **介绍**

一款基于uvicorn的web协程框架，目前仍处于开发阶段，一些基础功能已经可以使用。

目前仅保证支持python3.11。

## **功能**

1. 支持部分配置动态设置。

2. 起飞般的请求速度。

3. websocket支持。

4. 类Django的项目结构。

5. 外部模块导入。

## **安装**

```bash
pip install CheeseAPI
```

## **使用**

### **简单的示例**

创建一个入口文件：

```python
# File path: /app.py

from CheeseAPI import app, Request, Response

@app.route('/', [ 'GET' ])
async def index(request: Request):
    return Response('你好，这里是CheeseAPI！')
```

使用命令行启动服务器，你可以看到相应的信息打印在控制台上（默认为彩色打印）:

```bash
$ CheeseAPI --app app:app
(STARTING) 2023-08-01 00:44:11.143085 > Started CheeseAPI master process 92102
(STARTING) 2023-08-01 00:44:11.143122 > The application starts loading...
(STARTING) 2023-08-01 00:44:11.143133 > System information:
    system: MacOS
    python version: 3.11.4
    CheeseAPI version: 0.0.1
(STARTING) 2023-08-01 00:44:11.143142 > Workspace information:
    CheeseAPI path: /Users/cheese/Desktop/CheeseAPI/CheeseAPI
    base path: /Users/cheese/Desktop/CheeseAPI
(STARTING) 2023-08-01 00:44:11.143155 > Server information:
    host: 127.0.0.1
    port: 5214
    workers: 1
    is reload: False
    is debug: False
    is request logged: True
(STARTING) 2023-08-01 00:44:11.143215 > The server running on http://127.0.0.1:5214
(STARTING) 2023-08-01 00:44:11.153093 > The server started, took 0.009919 seconds
```

此时访问`GET http://127.0.0.1:5214`，会返回相应的`Response`。

### **项目结构**

CheeseAPI采用类Django的结构：

```
| - User
    | - model.py
    | - api.py
    | - service.py
    | - decorator.py
| - Permission
    | - model.py
    | - api.py
    | - service.py
    | - decorator.py
| - app.py
```

在项目根目录下的文件夹（不包括隐藏文件夹）内的文件会在项目启动时自动导入。

在CheeseAPI中并没有强制规定文件名与其代码的关联性，但建议的文件命名方式如下：

| 文件名 | 备注 |
| - | - |
| model.py | 模型类 |
| api.py | api接口 |
| service.py | 业务逻辑实现 |
| decorator.py | 装饰器 |

### **用户的增删改查**

该示例仅为演示，所用用户结构为普通的`class`构建，在正常项目中你应该使用`SQL`或`ORM`。

在开始，首先需要创建一个用户类：

```python
# File path: /User/model.py

import datetime, uuid
from enum import Enum
from typing import Optional

class Gender(Enum):
    MALE = 0
    FEMALE = 1
    UNKNOWN = 2

class User:
    def __init__(self, nickname: str, password: str, gender: Optional[Gender] = Gender.UNKNOWN):
        self.id: uuid.UUID = uuid.uuid4()
        self.nickname: str = nickname
        self.password: str = password
        self.gender: Gender = gender
        self.join_date: datetime.datetime = datetime.datetime.now()
```

实现增删改查的逻辑代码：

```python
# File path: /User/service.py

import uuid
from typing import Optional, Dict

from User.model import User, Gender

users: Dict[uuid.UUID, User] = {}
loginUsers: Dict[uuid.UUID, User] = {}

# 注册用户
def register(nickname: str, password: str, gender: Gender):
    user = User(nickname, password, gender)
    users[user.id] = user

# 登入用户
def login(nickname: str, password: str) -> User | None:
    for id, user in users.item():
        if user.nickname == nickname and user.password == password:
            loginUsers[id] = user
            return user
    return None

# 登出用户
def logout(id: uuid.UUID):
    if id in loginUsers:
        del loginUsers[id]

# 获取用户
def get_user(id: uuid.UUID) -> User | None:
    if id in users:
        return users[id]
    return None

# 修改用户信息
def set_user(id: uuid.UUID, nickname: str | None, password: str | None, gender: Gender | None) -> User | None:
    if id in users:
        user = users[id]
        if nickname:
            user.nickname = nickname
        if password:
            user.password = password
        if gender:
            user.gender = gender
        return user
    return None

# 删除用户
def delete_user(id: uuid.UUID) -> bool:
    if id in loginUsers:
        del loginUsers[id]
    if id in users:
        del users[id]
        return True
    return False
```

实现API接口，在实际项目中，你需要先进行数据的初步校验：

```python
# File path:

import uuid

from CheeseAPI import app, Request, Route, Response, JsonResponse

from User.model import Gender
from User import service

route = Route('/User', app.route)

@route.post('/register')
def register(request: Request):
    nickname = request.form.get('nickname')
    password = request.form.get('password')
    gender = Gender(request.form.get('gender', 2))
    service.register(nickname, password, gender)
    return Response('注册成功！')

@route.post('/login')
def login(request: Request):
    nickname = request.form.get('nickname')
    password = request.form.get('password')
    user = service.login(nickname, password)
    if user:
        return JsonResponse(user.__dict__)
    return Response('登入失败！', 401)

@route.post('/<id:uuid>/logout')
def logout(id: uuid.UUID):
    service.logout(id)
    return Response('登出成功！')

@route.get('/<id:uuid>')
def get_user(id: uuid.UUID):
    user = service.get_user(id)
    if user:
        return JsonResponse(user.__dict__)
    return Response('查找失败！', 404)

@route.put('/<id:uuid>')
def set_user(id: uuid.UUID):
    nickname = request.form.get('nickname')
    password = request.form.get('password')
    gender = request.form.get('gender')
    if gender:
        gender = Gender(gender)
    user = service.set_user(id, nickname, password, gender)
    if user:
        return JsonResponse(user.__dict__)
    return Response('修改信息失败！', 404)

@route.delete('/<id:uuid>')
def delete_user(id: uuid.UUID):
    flag = service.delete_user(id)
    if flag:
        return Response('删除用户成功！')
    return Response('删除用户失败！', 404)
```

这样，一个简陋的用户系统就搭建完成了，其中有很多纰漏例如会把密码返回出去 :(

## **更多...**

### 1. **[命令行](https://github.com/CheeseUnknown/CheeseAPI/tree/master/documents/command.md)**

### 2. **[详细配置](https://github.com/CheeseUnknown/CheeseAPI/tree/master/documents/detail.md)**

### 3. **[模块](https://github.com/CheeseUnknown/CheeseAPI/tree/master/documents/module.md)**

### 4. **[路由](https://github.com/CheeseUnknown/CheeseAPI/tree/master/documents/route.md)**

### 5. **[请求](https://github.com/CheeseUnknown/CheeseAPI/tree/master/documents/request.md)**

### 6. **[响应](https://github.com/CheeseUnknown/CheeseAPI/tree/master/documents/response.md)**

### 7. **[装饰器](https://github.com/CheeseUnknown/CheeseAPI/tree/master/documents/decorator.md)**

### 8. **[websocket](https://github.com/CheeseUnknown/CheeseAPI/tree/master/documents/websocket.md)**

### 9. **[信号](https://github.com/CheeseUnknown/CheeseAPI/tree/master/documents/signal.md)**

### 10. **[文件](https://github.com/CheeseUnknown/CheeseAPI/tree/master/documents/file.md)**
