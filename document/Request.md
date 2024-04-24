# **Request**

请求体；在每个路由的自定义函数都会传入该参数。

```python
from CheeseAPI import app, Request

@app.route.get('/')
async def index(*args, request: Request, **kwargs):
    ...
```

## **`request.fullPath: str`**

【只读】 完整路由，例如：`'/test?key1=value1&key2=value2'`。

## **`request.path: str`**

【只读】 不带参数的路由，例如：`'/test'`。

## **`request.scheme: Literal['http', 'https', 'ws', 'wss'] | None`**

【只读】 协议名称。

## **`request.url: str | None`**

【只读】 请求的完整地址，例如：`'http://127.0.0.1:5214/test?key1=value1&key2=value2'`。

## **`request.headers: Dict[str, str]`**

【只读】 请求的headers。

## **`request.args: Dict[str, str]`**

【只读】 路由中的query参数。

## **`request.method: http.HTTPMethod | Literal['WEBSOCKET']`**

【只读】 请求的method。

## **`request.origin: str | None`**

【只读】 请求的原始url地址。

## **`request.client: str | None`**

【只读】 请求的客户端ip。

## **`request.body: list | dict | str | bytes | None`**

【只读】 请求的body。

## **`request.form: Dict[str, str | File] | None`**

【只读】 从请求body中解析出的表单信息。

## **`request.cookie: Dict[str, str] | None`**

【只读】 从请求headers中解析出的cookie信息。

## **`request.subprotocols: List[str] | None`**

【只读】 Websocket可选的子协议；在http或websocket未提供子协议的时候为`None`。

## **`request.subprotocol: str | None`**

【只读】 Websocket选择的子协议；在http、websocket未提供子协议或选择子协议之前的时候为`None`。
