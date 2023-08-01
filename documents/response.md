# **响应**

在路由装饰器下，所有函数都必须返回一个`BaseResponse`。

## **`class Response(BaseResponse)`**

返回类型为`text/plain`的响应。

- **`def __init__(self, body: Any = '', status: int = 200, headers: Dict[str, str] = {})`**

## **`class JsonResponse(BaseResponse)`**

返回类型为`application/json`的响应。

- **`def __init__(self, body: Dict = {}, status: int = 200, headers: Dict[str, str] = {})`**

## **`class RedirectResponse(BaseResponse)`**

返回一个重定向响应。

- **`def __init__(self, url: str, status: int = 301, headers: Dict[str, str] = {})`**

## **`class FileResponse(BaseResponse)`**

返回一个文件响应。

- **`def __init__(self, file: File, isDownloaded: bool = False, headers: Dict[str, str] = {})`**

    默认的，文件可预览的话会优先预览，如果需要下载，则设置`isDownloaded = True`。

    `File`可看后续的《文件》一节。
