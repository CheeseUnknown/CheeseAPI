# **Response**

响应体；在每个路由的自定义函数都应当返回一个`BaseResponse`

## **`class BaseResponse`**

其他Response的父类；平时使用它判断response是否是合法的，并不建议使用它创建response

```python
from CheeseAPI import app, BaseResponse

@app.route.get('/')
async def index(*args, **kwargs):
    response = ...
    if isinstance(response, BaseResponse):
        ...
```

### **`def setCookie(self, key: str, value: str, *, path: str = '/', secure: bool = False, httpOnly: bool = False, domain: str = '', sameSite: Literal['Strict', 'Lax', 'None'] = 'Lax', expires: datetime.datetime | str | None = None, maxAge: datetime.timedelta | int | None = None)`**

设置cookie

## **`class Response(BaseResponse)`**

最基础的response

### **`def __init__(self, body: str | bytes | Callable | AsyncIterator | None = None, status: http.HTTPStatus | int = http.HTTPStatus.OK, headers: Dict[str, str] = {})`**

```python
from CheeseAPI import app, Response

@app.route.get('/')
async def index(*args, **kwargs):
    return Response('这里是CheeseAPI！')
```

## **`class JsonResponse(BaseResponse)`**

可将`dict`或`list`自动转为可发送的格式

### **`def __init__(self, body: dict | list = {}, status: http.HTTPStatus | int = http.HTTPStatus.OK, headers: Dict[str, str] = {})`**

```python
from CheeseAPI import app, JsonResponse

@app.route.get('/')
async def index(*args, **kwargs):
    return JsonResponse({
        'welcome': '这里是CheeseAPI！'
    })
```

## **`class FileResponse(BaseResponse)`**

文件响应体

### **`def __init__(self, path: str, headers: Dict[str, str] = {}, *, downloaded: bool = False, chunkSize: int = 1024 * 1024)`**

- **参数**

    - **path**

        文件路径；支持相对路径与绝对路径

    - **downloaded**

        文件是否下载；为`False`时优先预览，若无法预览则仍然下载

    - **chunkSize**

        发送文件的chunk大小

### **`def __init__(self, data: File, headers: Dict[str, str] = {}, *, downloaded: bool = False, chunkSize: int = 1024 * 1024)`**

- **参数**

    - **data**

        File实例

    - **downloaded**

        文件是否下载；为`False`时优先预览，若无法预览则仍然下载

    - **chunkSize**

        发送文件的chunk大小

## **`class RedirectResponse(BaseResponse)`**

重定向响应

### **`def __init__(self, location: str, status: http.HTTPStatus | int = http.HTTPStatus.FOUND, body: str | bytes | None = None, headers: Dict[str, str] = {})`**

- **参数**

    - **location**

        重定向的地址
