# **路由**

## **根路由**

根路由没有前缀，是最基础的路由。

```python
@app.route('/', [ 'GET' ])
async def get():
    ...
```

## **附属路由**

附属路由可以为另外的附属路由的子路由，它们的前缀会叠加。

```python
from CheeseAPI import Route

route1 = Route('/route1', app.route) # Prefix: /route1
route2 = Route('/route2', app.route) # Prefix: /route2
route11 = Route('/1', app.route) # Prefix: /route1/1

@route1('/abc', [ 'GET' ]) # /route1/abc
async def abc():
    ...
```

## **动态路由**

在下列代码中，当访问`GET /1`时，打印出了`1`：

```python
@app.route('/<id:int>', [ 'GET' ])
def a(id: int):
    print(id)
    ...
```

在格式为`<key:type>`的路由段中，会自动匹配类型符合的值，并返回变量。

动态路由有几个特点：

1. 如果路由同时满足固定路由和动态路由，则一定匹配固定路由。

2. 同时满足多个动态路由，匹配优先级最高，即动态路由段之前固定路由最多的那个，例如：

    请求：`GET /1/2`

    路由1: `GET /<id:int>/2`， 不匹配

    路由2：`GET /1/<id:int>`，匹配

3. 内置有`str`、`int`、`float`和`uuid`4种匹配类型，`str`是最后匹配的类型（兜底，啥都能匹配到）。

如果你想自定义匹配类型，你需要有一个正则匹配式和一个符合该类型的类。如果有冲突的正则，请将优先匹配的放在最后（当然要避免这种情况！）：

```python
from CheeseAPI.route import PATTERNS

class Pattern1:
    ...

PATTERNS['pattern1'] = {
    'pattern': r'假装是一个正则',
    'type': Pattern1
}
```

## **`class Route`**

路由有多种装饰器：

### **`@route(path: str, methods: List[str])`**

methods支持一次设置多种请求方式，同时支持`WEBSOCKET`。

```python
@route('/', [ 'GET', 'POST', 'WEBSOCKET' ])
async def abc():
    ...
```

使用了路由装饰器的函数，可以获取到动态路由的变量，以及`request`（变量不分顺序，可以选择不接收）：

```python
@route('/<id:uuid>', [ 'GET', 'POST', 'WEBSOCKET' ])
async def abc(request, id):
    ...
```

### **`@route.get(path: str)`**

设置一个`GET`请求，下列的装饰器都是设置单个请求方式。

### **`@route.post(path: str)`**

### **`@route.delete(path: str)`**

### **`@route.put(path: str)`**

### **`@route.patch(path: str)`**

### **`@route.websocket(path: str)`**
