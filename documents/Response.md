# **Response**

在HTTP以及部分WEBSOCKET特殊情况会返回Response，代表该[Request](./Request.md)已被响应。

```python
from CheeseAPI import Response, JsonResponse, FileResponse
```

## **`Response(body: str | bytes | Callable | None, status: http.HTTPStatus | int = http.HTTPStatus.OK, header: Dict[str, str] = {})`**

最基础的Response。

- **返回一个字符串**

    ```python
    from CheeseAPI import Response, app

    @app.route.get('/')
    async def test():
        return Response('Hello World')

- **返回字节**

    ```python
    from CheeseAPI import Response, app

    @app.route.get('/')
    async def test():
        return Response(b'Hello World')
    ```

- **返回一个回调函数**

    ```python
    from CheeseAPI import Response, app

    def callback():
        return 'Hello World'

    @app.route.get('/')
    async def test():
        return Response(callback)
    ```

- **返回迭代器，持续输出**

    ```python
    from CheeseAPI import Response, app

    async def iterator():
        for i in range(10):
            yield i

    @app.route.get('/')
    async def test():
        return Response(iterator)
    ```

## **`JsonResponse(body: Dict[str, Any] = {}, status: http.HTTPStatus | int = http.HTTPStatus.OK, header: Dict[str, str] = {})`**

它与`Response`唯一不同的是它会自动解析json格式的数据，不需要手动解析。

```python
from CheeseAPI import JsonResponse, app

@app.route.get('/')
async def test():
    return JsonResponse({
        'data': 'Hello World'
    })
```

## **`FileResponse(filePath: str, downloaded: bool = False, header: Dict[str, str] = {})`**

返回一个文件的Response。

- **`filePath: str`**

    若`filePath[0] == '.'`，会基于`app.workspace.base`路径查找文件，否则则使用绝对路径查找。

- **`downloaded: bool`**

    当`not downloaded`时，可预览的文件会优先预览，反正则进行下载操作。
