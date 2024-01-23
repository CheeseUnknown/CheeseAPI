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
async def test(**kwargs):
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
def test0(id: str, **kwargs):
    ...

@app.route.get('/<id:int>')
def test1(id: int, **kwargs):
    ...

@app.route.get('/<id:float>')
def test2(id: float, **kwargs):
    ...

@app.route.get('/<id:uuid>')
def test3(id: uuid.UUID, **kwargs):
    ...
```

在正常情况下，只有不满足其他的匹配条件，才会被`str`匹配到。

## **`@route(path: str, methods: List[ http.HTTPMethod | str ])`**

可同时为一个路由添加多个请求方法。

```python
from CheeseAPI import app

@app.route('/', [ 'GET', 'POST' ])
def test(**kwargs):
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

## **`def Route.addPattern(key: str, pattern: re.Pattern, type: object, weight: int)`**

添加自定义的动态匹配类型。

- `key`

    在路由中显示为`<id:[key]>`。

- `pattern`

    正则表达式，用于匹配对应的字符串。

- `type`

    自定义的类，必须有使用`MyType(value)`进行类型转换的功能。

- `weight`

    匹配权重，越大的值优先级越高。若正则表达式有冲突，请设置正确的权重以避免匹配错误。

    默认的动态匹配类型，`str`权重为0，其余权重为10。
