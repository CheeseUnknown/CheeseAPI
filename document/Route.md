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

通过装饰器添加一个路由：

```python
from CheeseAPI import Route

route = Route('/api')

@route('/test', 'POST')
async def test(**kwargs):
    ...
```

### **`def __call__(self, path: str, methods: List[ http.HTTPMethod | str ])`**

通过装饰器添加一个路由：

```python
from CheeseAPI import Route

route = Route('/api')

@route('/test', 'POST')
async def test(**kwargs):
    ...
```

### **`def __call__(self, path: str, methods: List[ http.HTTPMethod | str ], func: Callable)`**

通过函数添加一个路由：

```python
from CheeseAPI import Route

route = Route('/api')

async def test(**kwargs):
    ...

route('/test', 'POST'， test)
```

## **`def get(self, path: str)`**

通过装饰器添加一个GET路由（后续方法与此相同，不再重复）：

```python
from CheeseAPI import Route

route = Route('/api')

@route.get('/test')
async def test(**kwargs):
    ...
```

## **`def get(self, path: str, func: Callable)`**

通过函数添加一个GET路由（后续方法与此相同，不再重复）：

```python
from CheeseAPI import Route

route = Route('/api')

async def test(**kwargs):
    ...

route.get('/test', test)
```

## **`def post(self, path: str)`**

## **`def post(self, path: str, func: Callable)`**

## **`def delete(self, path: str)`**

## **`def delete(self, path: str, func: Callable)`**

## **`def put(self, path: str)`**

## **`def put(self, path: str, func: Callable)`**

## **`def patch(self, path: str)`**

## **`def patch(self, path: str, func: Callable)`**

## **`def trace(self, path: str)`**

## **`def trace(self, path: str, func: Callable)`**

## **`def options(self, path: str)`**

## **`def options(self, path: str, func: Callable)`**

## **`def head(self, path: str)`**

## **`def head(self, path: str, func: Callable)`**

## **`def connect(self, path: str)`**

## **`def connect(self, path: str, func: Callable)`**

## **`def websocket(self, path: str)`**

该方式调用与http路由不同，具体请查看[Websocket](./Websocket.md)。

## **`def websocket(self, path: str, func: WebsocketServer)`**

该方式调用与http路由不同，具体请查看[Websocket](./Websocket.md)。
