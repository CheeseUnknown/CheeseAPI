# **Route**

路由。

## **`class Route`**

CheeseAPI提供一个基础路由：

```python
from CheeseAPI import app

app.route
```

### **`def __init__(self, prefix: str = '')`**

初始化一个有前缀的路由：

```python
from CheeseAPI import Route

route = Route('/api')
```

### **`def __call__(self, path: str, methods: List[ http.HTTPMethod | str ])`**

添加一个路由：

```python
from CheeseAPI import Route

route = Route('/api')

@route('/test', 'POST')
async def test(**kwargs):
    ...
```

## **`def get(self, path: str)`**

添加一个GET路由（后续调用方法与此相同，不再重复）：

```python
from CheeseAPI import Route

route = Route('/api')

@route.get('/test')
async def test(**kwargs):
    ...
```

## **`def post(self, path: str)`**

添加一个POST路由。

## **`def delete(self, path: str)`**

添加一个DELETE路由。

## **`def put(self, path: str)`**

添加一个PUT路由。

## **`def patch(self, path: str)`**

添加一个PATCH路由。

## **`def trace(self, path: str)`**

添加一个TRACE路由。

## **`def options(self, path: str)`**

添加一个OPTIONS路由。

## **`def head(self, path: str)`**

添加一个HEAD路由。

## **`def connect(self, path: str)`**

添加一个CONNECT路由。

## **`def websocket(self, path: str)`**

添加一个WEBSOCKET路由。

该方式调用与http路由不同，具体请查看[Websocket](./Websocket.md)。
