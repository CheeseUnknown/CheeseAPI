# **Route**

路由是CheeseAPI的基础，`app`自带一个基础路由：

```python
from CheeseAPI import app

app.route
```

## **路由前缀**

在模块中使用路由前缀可以更好的管理api接口。

```python
from CheeseAPI import Route

route = Route('/test')

@route.get('/0')
async def test():
    ...
```

访问`GET /test/0`即可。

在本质上来说，`route`只是比`app.route`多了前缀`'/test'`。

## **动态路由**

CheeseAPI默认支持`str`、`int`、`float`和`uuid`的动态匹配类型。

```python
import uuid

from CheeseAPI import app

@app.route.get('/<id:str>')
def test0(id: str):
    ...

@app.route.get('/<id:int>')
def test1(id: int):
    ...

@app.route.get('/<id:float>')
def test2(id: float):
    ...

@app.route.get('/<id:uuid>')
def test3(id: uuid.UUID):
    ...
```

在正常情况下，只有不满足其他的匹配条件，才会被`str`匹配到。

## **`@route(path: str, methods: List[ http.HTTPMethod | str ])`**

可同时为一个路由添加多个请求方法。

```python
from CheeseAPI import app

@app.route('/', [ 'GET', 'POST' ])
def test():
    ...
```

## **`@route.get(path: str)`**

为路由添加一个GET方法。

## **`@route.post(path: str)`**

为路由添加一个POST方法。

## **`@route.delete(path: str)`**

为路由添加一个DELETE方法。

## **`@route.put(path: str)`**

为路由添加一个PUT方法。

## **`@route.patch(path: str)`**

为路由添加一个PATCH方法。

## **`@route.trace(path: str)`**

为路由添加一个TRACE方法。

## **`@route.options(path: str)`**

为路由添加一个OPTIONS方法。

## **`@route.head(path: str)`**

为路由添加一个HEAD方法。

## **`@route.connect(path: str)`**

为路由添加一个CONNECT方法。

## **`@route.websocket(path: str)`**

为路由添加一个WEBSOCKET方法。

该方法与其他不同，因为WEBSOCKET的构建方式与HTTP请求有异，具体请查看[Websocket](./Websocket.md)。
