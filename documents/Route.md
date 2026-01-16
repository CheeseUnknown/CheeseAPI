# **路由**

路由分为隶属于 app 的总路由，和自定义的子路由

## **子路由**

```python
from CheeseAPI import Route

from app import app

route = Route('/custom_path', app)
```

### **`def __init__(self, path: str, app: 'CheeseAPI')`**

- **Args**

    - **path**

        路由前缀

### **`self.path: str`**

路由前缀

### **`def add(self, method_or_methods: list[HTTP_METHOD_TYPE] | HTTP_METHOD_TYPE, path: str, fn: Callable | 'Websocket' | AsyncIterable | None = None, *, allow_origins: list[str] | None = None, allow_methods: list[HTTP_METHOD_TYPE] | None = None, allow_headers: list[str] | None = None, allow_credentials: bool | None = None, expose_headers: list[str] | None = None, max_age: int | None = None, auto_recv_body: bool = True)`**

- **Args**

    - **auto_recv_body**

        是否自动接收响应的 body，若否则自行调用 `request.recv_body()` 接收，并自行调用 `request.parse_body()` 解析

### **`def get(self, path: str, fn: Callable | AsyncIterable | None = None, *, allow_origins: list[str] | None = None, allow_methods: list[HTTP_METHOD_TYPE] | None = None, allow_headers: list[str] | None = None, allow_credentials: bool | None = None, expose_headers: list[str] | None = None, max_age: int | None = None, auto_recv_body: bool = True)`**

- **Args**

    - **auto_recv_body**

        是否自动接收响应的 body，若否则自行调用 `request.recv_body()` 接收，并自行调用 `request.parse_body()` 解析

### **`def post(self, path: str, fn: Callable | AsyncIterable | None = None, *, allow_origins: list[str] | None = None, allow_methods: list[HTTP_METHOD_TYPE] | None = None, allow_headers: list[str] | None = None, allow_credentials: bool | None = None, expose_headers: list[str] | None = None, max_age: int | None = None, auto_recv_body: bool = True)`**

- **Args**

    - **auto_recv_body**

        是否自动接收响应的 body，若否则自行调用 `request.recv_body()` 接收，并自行调用 `request.parse_body()` 解析

### **`def websocket(self, path: str, fn: Union['Websocket', None] = None, *, allow_origins: list[str] | None = None, allow_methods: list[HTTP_METHOD_TYPE] | None = None, allow_headers: list[str] | None = None, allow_credentials: bool | None = None, expose_headers: list[str] | None = None, max_age: int | None = None)`**

### **`def delete(self, path: str, fn: Callable | AsyncIterable | None = None, *, allow_origins: list[str] | None = None, allow_methods: list[HTTP_METHOD_TYPE] | None = None, allow_headers: list[str] | None = None, allow_credentials: bool | None = None, expose_headers: list[str] | None = None, max_age: int | None = None, auto_recv_body: bool = True)`**

- **Args**

    - **auto_recv_body**

        是否自动接收响应的 body，若否则自行调用 `request.recv_body()` 接收，并自行调用 `request.parse_body()` 解析

### **`def put(self, path: str, fn: Callable | AsyncIterable | None = None, *, allow_origins: list[str] | None = None, allow_methods: list[HTTP_METHOD_TYPE] | None = None, allow_headers: list[str] | None = None, allow_credentials: bool | None = None, expose_headers: list[str] | None = None, max_age: int | None = None, auto_recv_body: bool = True)`**

- **Args**

    - **auto_recv_body**

        是否自动接收响应的 body，若否则自行调用 `request.recv_body()` 接收，并自行调用 `request.parse_body()` 解析

### **`def patch(self, path: str, fn: Callable | AsyncIterable | None = None, *, allow_origins: list[str] | None = None, allow_methods: list[HTTP_METHOD_TYPE] | None = None, allow_headers: list[str] | None = None, allow_credentials: bool | None = None, expose_headers: list[str] | None = None, max_age: int | None = None, auto_recv_body: bool = True)`**

- **Args**

    - **auto_recv_body**

        是否自动接收响应的 body，若否则自行调用 `request.recv_body()` 接收，并自行调用 `request.parse_body()` 解析

### **`def head(self, path: str, fn: Callable | AsyncIterable | None = None, *, allow_origins: list[str] | None = None, allow_methods: list[HTTP_METHOD_TYPE] | None = None, allow_headers: list[str] | None = None, allow_credentials: bool | None = None, expose_headers: list[str] | None = None, max_age: int | None = None, auto_recv_body: bool = True)`**

- **Args**

    - **auto_recv_body**

        是否自动接收响应的 body，若否则自行调用 `request.recv_body()` 接收，并自行调用 `request.parse_body()` 解析

### **`def options(self, path: str, fn: Callable | AsyncIterable | None = None, *, allow_origins: list[str] | None = None, allow_methods: list[HTTP_METHOD_TYPE] | None = None, allow_headers: list[str] | None = None, allow_credentials: bool | None = None, expose_headers: list[str] | None = None, max_age: int | None = None, auto_recv_body: bool = True)`**

- **Args**

    - **auto_recv_body**

        是否自动接收响应的 body，若否则自行调用 `request.recv_body()` 接收，并自行调用 `request.parse_body()` 解析

### **`def trace(self, path: str, fn: Callable | AsyncIterable | None = None, *, allow_origins: list[str] | None = None, allow_methods: list[HTTP_METHOD_TYPE] | None = None, allow_headers: list[str] | None = None, allow_credentials: bool | None = None, expose_headers: list[str] | None = None, max_age: int | None = None, auto_recv_body: bool = True)`**

- **Args**

    - **auto_recv_body**

        是否自动接收响应的 body，若否则自行调用 `request.recv_body()` 接收，并自行调用 `request.parse_body()` 解析

### **`def connect(self, path: str, fn: Callable | AsyncIterable | None = None, *, allow_origins: list[str] | None = None, allow_methods: list[HTTP_METHOD_TYPE] | None = None, allow_headers: list[str] | None = None, allow_credentials: bool | None = None, expose_headers: list[str] | None = None, max_age: int | None = None, auto_recv_body: bool = True)`**

- **Args**

    - **auto_recv_body**

        是否自动接收响应的 body，若否则自行调用 `request.recv_body()` 接收，并自行调用 `request.parse_body()` 解析

## **总路由**

总路由隶属于 app，无需手动创建；总路由继承于 `Route`，可直接使用子路由的所有方法

```python
from CheeseAPI import CheeseAPI

app = CheeseAPI()
route = app.route
```

### **`patterns: list[Pattern]`**

动态路由匹配模式

### **`routes: dict[str, dict['GET' | 'POST' | ..., RouteDict]]`**

所有路由
