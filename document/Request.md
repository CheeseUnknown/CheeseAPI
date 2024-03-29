# **Request**

请求体；在每个路由的自定义函数都会传入该参数。

```python
from CheeseAPI import app, Request

@app.route.get('/')
async def index(*args, request: Request, **kwargs):
    ...
```

## **`request.fullPath: str`**

完整路由，例如：`'/test?key1=value1&key2=value2'`。

## **`request.path: str`**

不带参数的路由，例如：`'/test'`。

## **`request.scheme: Literal['http', 'https', 'ws', 'wss'] | None`**

协议名称。

## **`request.url: str | None`**

请求的完整地址，例如：`'http://127.0.0.1:5214/test?key1=value1&key2=value2'`。

## **`request.headers: Dict[str, str]`**

请求的headers。

## **`request.args: Dict[str, str]`**

路由中的query参数。

## **`request.method: http.HTTPMethod | Literal['WEBSOCKET']`**

请求的method。

## **`request.origin: str | None`**

请求的原始url地址。

## **`request.client: str | None`**

请求的客户端ip。

## **`request.body: list | dict | str | bytes | None`**

请求的body；在websocket请求中为`None`。

## **`request.form: Dict[str, str | File] | None`**

从请求body中解析出的表单信息；在websocket请求中为`None`。

## **`request.subprotocols: List[str] | None`**

Websocket可选的子协议；在http或websocket未提供子协议的时候为`None`。

## **`request.subprotocol: str | None`**

Websocket选择的子协议；在http、websocket未提供子协议或选择子协议之前的时候为`None`。
