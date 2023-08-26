# **Request**

```python
from CheeseAPI import app, Request, WebsocketClient

@app.route.get('/')
async def test(request: Request):
    ...

@app.route.websocket('/')
class Test(WebsocketClient):
    async def connect(request: Request):
        ...

    async def data(request: Request):
        ...

    async def disconnect(request: Request):
        ...
```

## **`request.url: str`**

当前访问的完整url地址，例如`'http://192.168.1.2:5214/test?arg=0'`。

## **`request.path: str`**

例如：`'/test'`

## **`request.fullPath: str`**

例如：`'/test?arg=0'`。当url中没有额外参数时，它与`request.path`相同。

## **`request.scheme: Literal[ 'http', 'https', 'ws', 'wws' ]`**

当前请求的类型。

## **`request.header: Dict[str, str]`**

请求头。

## **`request.query: Dict[str, str]`**

url中的参数，例如：`'{ 'test': '0' }'`。

## **`request.method: http.HTTPMethod`**

在WEBSOCKET环境下，该参数不存在。

## **`request.body: str | bytes`**

在WEBSOCKET环境下，该参数不存在。

除去`request.header['Content-Type'] in [ 'multipart/form-data', 'x-www-form-urlencoded' ]`，其他都会解析在此处。

## **`request.form: Dict[str, str]`**

在WEBSOCKET环境下，该参数不存在。

会将`request.header['Content-Type'] in [ 'multipart/form-data', 'x-www-form-urlencoded' ]`的类型解析在此处。
